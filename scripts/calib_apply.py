"""Áp quyết định calibration (guideline v1.1) lên nhãn độc lập của 101/102/142 → COCO sau sửa cho 40 ảnh.

Chạy: python scripts/calib_apply.py <out.json> > submission/qc/calib_apply.log
Quy tắc áp (khớp calibration_decisions.csv):
- Box ghép được giữa 2 người: box trung bình (R-01); lớp theo đa số, ca sai_lop theo quyết định từng case (R-05/R-06).
- occluded_level: lệch thì lấy mức cao hơn (R-11). truncated: theo hình học, cạnh box cách mép ảnh <= 2 px (R-12).
- can_review: bỏ hết sau khi chốt (R-19).
- Box chỉ 1 người vẽ: giữ nếu cao >= 20 px (R-14); ở ảnh đám đông R-15 (CROWD_IGNORE) bỏ nếu nằm trong ignore_region của người kia.
- ignore_region: gộp vùng trùng (IoU >= 0.3) thành box trung bình; vùng đơn lẻ vẫn giữ (R-15).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from common import (QC_DIR, area, build_coco, inter_area, cluster_objects, covered_by, iou, load_all_labels, load_taxonomy,  # noqa: E402
                    make_ann, mean_box, read_csv, require_assignment, xywh_to_xyxy)

tax = load_taxonomy()
files = load_all_labels(tax)
assignment = require_assignment()
cands = read_csv(QC_DIR / "calibration_candidates.csv")
MIN_H = tax.rules["min_box_height_px"]

# Quyết định lớp cho các ca sai_lop (xem ảnh gốc): case_id -> lớp chốt, hoặc "split" (2 vật khác nhau)
CLASS_DECISION = {
    "C068": "car", "C069": "van", "C163": "car", "C214": "car", "C215": "car", "C273": "car",
    "C480": "truck", "C486": "bus", "C515": "tuk_tuk", "C516": "tuk_tuk", "C129": "split",
}
GROUP = {c: 'vehicle' for c in ('car', 'van', 'truck', 'bus', 'tuk_tuk')} | {'person': 'person', 'motorcycle': 'motorcycle'}
# Ảnh guideline v1.0 R-15 nêu rõ cụm đám đông / xe dày → ignore_region; chỉ ở đây box đơn lẻ nằm trong
# ignore của người kia mới bị bỏ. Ảnh khác: vật >= 20 px tách được vẫn phải box (R-14/R-15).
CROWD_IGNORE = {"img_001.jpg", "img_003.jpg", "img_019.jpg", "img_021.jpg", "img_025.jpg", "img_030.jpg", "img_032.jpg"}
# Lỗi 'cả hai cùng sai' (IAA không bắt được), sửa theo bảng ca khó guideline mục 4.2: (ảnh, box xyxy) -> lớp
GUIDELINE_FIX = {("img_012.jpg", (288, 245, 959, 640)): "truck"}  # pickup chở hàng tiền cảnh → truck (R-05)
# Lỗi QC vòng 1 (submission/qc/reviews/round-01/qc_review.csv) → Rework: (mã, ảnh, box xyxy, hành động)
QC_FIX = [
    ("Q01", "img_007.jpg", (340, 296, 358, 321), "drop"),          # vật trên bàn bị gán person (R-08)
    ("Q02", "img_014.jpg", (2, 402, 264, 659), "motorcycle"),      # vệt mờ là xe máy, không phải car (R-17)
    ("Q03", "img_018.jpg", (212, 207, 317, 333), "drop"),          # chân dung trên pano (R-08)
    ("Q04", "img_024.jpg", (239, 45, 701, 251), "drop"),           # vỏ xe vàng trên nóc (R-10)
    ("Q05", "img_028.jpg", (35, 245, 879, 693), (35, 298, 925, 693)),  # box truck không kéo lên tượng ngựa (R-10)
]
# Ca chọn box của một người thay vì trung bình (box người kia thiếu/thừa phần vật)
BOX_FROM = {"C069": "101", "C516": "142"}


def case_for(img, cluster):
    for c in cands:
        if c["image"] != img or c["case_id"] not in CLASS_DECISION:
            continue
        cb = [xywh_to_xyxy(json.loads(b)) for b in (c["box_a"], c["box_b"]) if b]
        if any(iou(o.box, b) > 0.9 for o in cluster.values() for b in cb):
            return c["case_id"]
    return None


def attrs_of_box(at, box, W, H):
    at = dict(at)
    at["truncated"] = "yes" if (box[0] <= 2 or box[1] <= 2 or box[2] >= W - 2 or box[3] >= H - 2) else "no"
    return at


def attrs_of(objs, box, W, H):
    occ = max(int(o.attrs["occluded_level"]) for o in objs)
    trunc = "yes" if (box[0] <= 2 or box[1] <= 2 or box[2] >= W - 2 or box[3] >= H - 2) else "no"
    return {"occluded_level": str(occ), "truncated": trunc, "can_review": "false"}


images, anns, log = [], [], []
for iid, img in enumerate(sorted(assignment), 1):
    members = sorted(assignment[img])
    W, H = files[members[0]].images[img]
    images.append({"id": iid, "file_name": img, "width": W, "height": H})
    ign = {m: [o.box for o in files[m].objects[img] if o.cls == tax.ignore] for m in members}
    objs = {m: [o for o in files[m].objects[img] if o.cls != tax.ignore] for m in members}
    out = []
    for cl in cluster_objects(objs, tax.rules["match_iou"]):
        if len(cl) == 1:
            (m, o), = cl.items()
            others = [x for x in members if x != m]
            if o.box[3] - o.box[1] < MIN_H:
                log.append(f"{img}: bỏ {o.cls} của {m} (cao < {MIN_H}px)"); continue
            if img in CROWD_IGNORE and any(covered_by(o.box, ign[x]) for x in others):
                log.append(f"{img}: bỏ {o.cls} của {m} (nằm trong ignore_region của người kia)"); continue
            out.append((o.cls, o.box, attrs_of([o], o.box, W, H), m))
            continue
        classes = {o.cls for o in cl.values()}
        case = case_for(img, cl) if len(classes) > 1 else None
        if case and CLASS_DECISION[case] == "split":
            for o in cl.values():
                out.append((o.cls, o.box, attrs_of([o], o.box, W, H), None))
            log.append(f"{img}: {case} tách thành {sorted(classes)}"); continue
        box = cl[BOX_FROM[case]].box if case in BOX_FROM else mean_box([o.box for o in cl.values()])
        if case:
            cls = CLASS_DECISION[case]
            log.append(f"{img}: {case} chốt lớp {cls}")
        elif len(classes) == 1:
            cls = classes.pop()
        else:
            raise SystemExit(f"{img}: lớp lệch {classes} chưa có quyết định")
        out.append((cls, box, attrs_of(list(cl.values()), box, W, H), set(cl)))
    # R-20: một vật một box. Box đơn lẻ (1 người vẽ) trùng vật với box đã ghép cùng nhóm lớp → bỏ.
    paired = [(c, b, src) for c, b, _, src in out if not isinstance(src, str)]
    kept = []
    for cls, box, at, single in out:
        if isinstance(single, str):
            dup = next((pc for pc, pb, _ in paired if GROUP.get(pc) == GROUP.get(cls)
                        and min(area(box), area(pb)) >= 0.25 * max(area(box), area(pb))  # cỡ tương đương (R-10: car nhỏ trong truck vẫn giữ)
                        and inter_area(box, pb) > 0.6 * min(area(box), area(pb))), None)
            # mảnh vỡ: cùng người, cùng lớp, nằm gọn (>90%) trong box mà chính người đó đã góp vào cụm ghép
            dup = dup or next((pc for pc, pb, src in paired if pc == cls and src and single in src
                               and inter_area(box, pb) > 0.9 * area(box)
                               and area(box) >= 0.1 * area(pb)), None)  # vật nhỏ ở xa nằm trong box vẫn giữ
            if dup:
                log.append(f"{img}: bỏ {cls} {[int(v) for v in box]} (trùng vật với box {dup} đã ghép, R-20)")
                continue
        fix = next((c for (fi, fb), c in GUIDELINE_FIX.items() if fi == img and iou(box, fb) > 0.8), None)
        if fix and fix != cls:
            log.append(f"{img}: đổi {cls} → {fix} {[int(v) for v in box]} (cả hai người cùng sai, theo guideline)")
            cls = fix
        q = next(((qid, act) for qid, qi, qb, act in QC_FIX if qi == img and iou(box, qb) > 0.8), None)
        if q:
            qid, act = q
            if act == "drop":
                log.append(f"{img}: {qid} xóa {cls} {[int(v) for v in box]} (QC vòng 1)"); continue
            if isinstance(act, str):
                log.append(f"{img}: {qid} đổi {cls} → {act} (QC vòng 1)"); cls = act
            else:
                log.append(f"{img}: {qid} sửa box {cls} {[int(v) for v in box]} → {list(act)} (QC vòng 1)"); box = act
                at = attrs_of_box(at, box, W, H)
        kept.append((cls, box, at))
    out = kept
    for cl in cluster_objects({m: [o for o in files[m].objects[img] if o.cls == tax.ignore] for m in members}, 0.3):
        out.append((tax.ignore, mean_box([o.box for o in cl.values()]), {}))
    for cls, box, at in out:
        anns.append(make_ann(tax, len(anns) + 1, iid, cls, box, at))

coco = build_coco(tax, images, anns, {"description": "Nhãn sau calibration v1.1 (áp quyết định calibration_decisions.csv)"})
Path(sys.argv[1]).write_text(json.dumps(coco, ensure_ascii=False, indent=1), encoding="utf8")
print(f"{len(images)} ảnh, {len(anns)} annotation")
print("\n".join(log))
