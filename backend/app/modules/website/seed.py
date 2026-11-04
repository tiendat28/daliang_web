"""Noi dung mac dinh cua website cong khai (daliang.com).

Website khong co bang noi dung rieng: san pham la cac ma trong
common.company_products co web_group. File nay chi:
  - chon 18 ma dua len web (6 ma moi nhom) - CHI lam khi chua ma nao duoc
    chon, de ma nguoi dung da go khoi web khong tu hien lai sau moi lan khoi dong;
  - dien ten tieng Trung, mo ta tieng Viet/Anh/Trung cho cac ma do - chi o con trong.
Thong tin lien he mac dinh nam o app.modules.common.service.

Chay tu dong luc backend khoi dong; chay tay:
    docker compose exec backend python -m app.modules.website.seed
"""
from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.modules import load_all_modules
from app.modules.common import models as common_models

# (ma, nhom, ten tieng Trung, mo ta tieng Viet, mo ta tieng Anh, mo ta tieng Trung)
WEB_PRODUCTS = [
    ("DU-252", "pre", "电解除油剂",
     "Bột tẩy dầu điện phân có khả năng nhũ hóa mạnh, loại bỏ nhiều loại dầu mỡ. Có thể gia nhiệt để dùng cho công đoạn nhúng nóng. Dùng được cho cả mạ treo và mạ quay.",
     "Electro-cleaning powder with strong emulsifying power that removes a wide range of oils. Can be heated for hot soak cleaning; suits both rack and barrel lines.",
     "乳化力强的电解除油粉，可去除多种油脂；可加温用于热浸除油，挂镀、滚镀皆适用。"),
    ("DU-55", "pre", "浸泡除油剂",
     "Hiệu quả cao loại bỏ dầu động thực vật, dầu khoáng, dầu chống gỉ, dầu gia công kim loại và cặn đánh bóng/mài rung. Chịu axit/kiềm tốt, tuổi thọ dài.",
     "Removes vegetable, mineral, anti-rust and machining oils as well as polishing and vibratory residues. Tolerates acid and alkali well with a long bath life.",
     "高效去除动植物油、矿物油、防锈油、金属加工油及抛光/振磨残渣；耐酸碱，槽液寿命长。"),
    ("DU-140", "pre", "超声波除油剂",
     "Bột tẩy dầu đa năng dùng cho nhúng nóng kết hợp siêu âm, không ăn mòn nền. Kiềm thấp, nhũ hóa tốt, ít bọt, dễ rửa.",
     "Multi-purpose powder for hot soak cleaning combined with ultrasonics, non-etching to the substrate. Low alkalinity, good emulsification, low foam, easy to rinse.",
     "适用于热浸配合超声波的多功能除油粉，不腐蚀基材；低碱、乳化好、低泡、易水洗。"),
    ("DU-691", "pre", "除锈剂",
     "Kết hợp tẩy dầu kiềm và tẩy gỉ axit trong 1 thao tác, loại bỏ hoàn toàn dầu và bẩn đen từ nấu chảy/hàn. Hiệu quả tẩy dầu vượt trội, rút ngắn thời gian xử lý.",
     "Combines alkaline degreasing and acid pickling in one step, fully removing oil and the black smut left by melting or welding. Shortens the treatment time.",
     "一步完成碱性除油与酸性除锈，彻底去除油污及熔炼、焊接留下的黑渍，缩短处理时间。"),
    ("AC-345", "pre", "活化盐",
     "Bột muối axit dạng rắn, an toàn khi bảo quản, dùng bóc crom không thụ động lớp niken và không ảnh hưởng bám dính. Tuổi thọ dài.",
     "Solid acid salt that is safe to store. Strips chromium without passivating the nickel layer and without affecting adhesion. Long bath life.",
     "固体酸盐，储存安全；退铬时不钝化镍层，不影响结合力，槽液寿命长。"),
    ("AM-948", "pre", "沉锌剂",
     "Dùng cho nhiều hợp kim nhôm và dây chuyền tự động, hiệu quả tốt với hợp kim đúc bề mặt nhám cao, tạo màng kẽm đồng đều đảm bảo bám dính tối ưu.",
     "Zincate for many aluminium alloys and automatic lines, effective on rough die-cast surfaces; forms an even zinc film for optimum adhesion.",
     "适用于多种铝合金及自动线，对表面粗糙的压铸件效果佳，形成均匀锌膜，确保最佳结合力。"),
    ("NCZ-48", "add", "无氰碱性镀锌添加剂",
     "Dùng trực tiếp không cần chất khởi động riêng, chất lượng ổn định; tạo thụ động xanh óng ánh; ứng suất nội thấp, độ dẻo và bám dính tốt, tinh thể mịn; chống ăn mòn cao, phủ và phân tán tốt.",
     "Ready to use without a separate starter, with stable quality. Gives bright blue passivation, low internal stress, good ductility and adhesion, fine grain, high corrosion resistance and good throwing power.",
     "无需单独开缸剂，品质稳定；钝化后呈亮蓝色，内应力低、延展性与结合力好、结晶细致，耐蚀性高，分散能力佳。"),
    ("NCZ-35", "add", "碱性锌镍合金添加剂",
     "Chịu nhiệt và chống ăn mòn tốt; lớp mạ óng ánh trong suốt, tương thích với cả thụ động đen và thụ động thường; phù hợp cho cả mạ treo và mạ quay; có ứng dụng bổ sung tăng cường độ chống ăn mòn. Đáp ứng yêu cầu RoHS, không chứa Pb, Cd, Hg, Cr⁶⁺, PBB và PBDE.",
     "Heat- and corrosion-resistant, clear iridescent deposit compatible with black and standard passivates, for rack and barrel. RoHS compliant — free of Pb, Cd, Hg, Cr⁶⁺, PBB and PBDE.",
     "耐热、耐蚀，镀层透明彩亮，兼容黑色及常规钝化，挂镀、滚镀皆可；符合 RoHS，不含铅、镉、汞、六价铬、PBB 及 PBDE。"),
    ("ZK-830", "add", "氯化物酸性镀锌添加剂",
     "Dải mật độ dòng rộng, san phẳng vượt trội, hiệu suất dòng gần 100%, mạ sâu tốt, ổn định cao, dùng chung được hệ kali và amoni; ít giòn hydro, phù hợp mạ trực tiếp thép đúc/nhiệt luyện, vít, bulong, đinh tán và chi tiết lỗ mù.",
     "Wide current density range, excellent levelling, near 100% current efficiency and good deep plating. Works in potassium or ammonium baths with low hydrogen embrittlement — suited to cast steel, screws, bolts and blind holes.",
     "电流密度范围宽，整平性优异，电流效率近 100%，深镀能力好；钾盐、铵盐体系通用，氢脆低，适用于铸钢、螺丝、螺栓及盲孔件。"),
    ("NG-66E", "add", "光亮镀镍添加剂",
     "Bề mặt bóng bắt mắt, san phẳng vượt trội, độ dẻo tốt, chi phí thấp; ái lực cao với lớp niken bán bóng trong hệ niken nhiều lớp, đạt kết quả tốt trong thử nghiệm CASS, không chứa chất phá hủy tầng ozon.",
     "Brilliant bright finish with outstanding levelling, good ductility and low cost. Strong affinity to semi-bright nickel in multi-layer systems, good CASS results, free of ozone-depleting substances.",
     "外观光亮夺目，整平性卓越，延展性好，成本低；在多层镍体系中与半光亮镍结合良好，CASS 测试表现佳，不含破坏臭氧层物质。"),
    ("810", "add", "酸性光亮镀铜添加剂",
     "Dải dòng điện rộng, san phẳng tốt, bóng gương, không rỗ khí khi dùng lâu dài. Tốc độ mạ nhanh, ứng suất nội thấp, độ dẻo cao, dung dịch ổn định, dễ quản lý.",
     "Wide current range, good levelling and mirror brightness with no pitting over long use. Fast plating, low stress, high ductility, and a stable bath that is easy to control.",
     "电流范围宽，整平好，镜面光亮，长期使用无针孔；沉积快、应力低、延展性高，槽液稳定易管理。"),
    ("G-TB", "add", "硫酸盐光亮镀锡添加剂",
     "Tạo lớp mạ bóng tuyệt đối; độ dẻo và khả năng hàn vượt trội; độ đồng đều bề mặt và chống ăn mòn tốt; phù hợp mạ treo, mạ quay tốc độ cao. Đạt kết quả hàn tốt trong kiểm nghiệm phòng thí nghiệm.",
     "Fully bright tin deposit with excellent ductility and solderability, good uniformity and corrosion resistance. Suits rack and high-speed barrel plating.",
     "镀层全光亮，延展性与可焊性优异，均匀性及耐蚀性好；适用于挂镀及高速滚镀。"),
    ("BK-25", "pas", "三价铬蓝白钝化剂",
     "Dung dịch thụ động xanh trắng crom 3+; thời gian xuất hiện gỉ trắng trong thử nghiệm phun muối trung tính đạt từ 25–48 giờ.",
     "Similar to BK-25L; white rust appears after about 25–48 hours in neutral salt spray.",
     "与 BK-25L 相似；中性盐雾测试约 25–48 小时出现白锈。"),
    ("CRT-150", "pas", "三价铬高耐蚀彩色钝化剂",
     "Vận hành ở nhiệt độ thấp giúp tiết kiệm năng lượng; đạt độ chống ăn mòn cao tương đương thụ động vàng crom 6+; đáp ứng tiêu chuẩn End-of-Life Vehicle (ELV).",
     "Runs at low temperature to save energy, reaches corrosion resistance comparable to yellow hexavalent chromate and meets End-of-Life Vehicle (ELV) requirements.",
     "低温操作、节能，耐蚀性可与六价铬黄色钝化相当，符合 ELV 报废车辆指令。"),
    ("CHB-60", "pas", "三价铬亮黑钝化剂",
     "Không chứa crom 6+, phù hợp cho cả mạ treo và mạ quay, tạo lớp mạ đen bóng đồng đều; kết hợp chất bịt kín CHB-19 đạt từ 48–96 giờ kháng gỉ trắng.",
     "Free of Cr⁶⁺, for rack and barrel, giving an even bright black. With CHB-19 it reaches 48–96 h to white rust.",
     "不含六价铬，挂镀、滚镀皆可，黑色均匀光亮；配合 CHB-19 可达 48–96 小时白锈。"),
    ("CHB-215", "pas", "三价铬黑色钝化剂",
     "Không chứa crom 6+, công thức chuyên biệt cho kẽm axit và kẽm kiềm không xyanua, khác biệt với thụ động muối niken thông thường; có khả năng tự phục hồi vết xước trên dây chuyền tự động; kết hợp CHB-19 đạt từ 72–120 giờ kháng gỉ trắng.",
     "Cr⁶⁺-free formula for acid and cyanide-free alkaline zinc, unlike common nickel-salt passivates; can repair scuffs on rack and automatic lines. With CHB-19 it reaches 72–120 h to white rust.",
     "不含六价铬，专为酸性锌及无氰碱性锌配方，有别于常规镍盐钝化；可修复挂镀或自动线上的碰擦痕；配合 CHB-19 可达 72–120 小时白锈。"),
    ("ELV-C5000", "pas", "锌镍合金三价铬彩色钝化剂",
     "Thụ động crom 3+ ngũ sắc cho lớp mạ kẽm-niken (12–15% Ni), chịu nhiệt và chống ăn mòn vượt trội; có thể kết hợp chất bịt kín hữu cơ để tăng cường bảo vệ mà vẫn giữ màu sắc nguyên bản.",
     "Trivalent iridescent passivate for zinc-nickel deposits (12–15% Ni) with good heat resistance; can be topped with an organic sealer for extra protection while keeping the original colour.",
     "用于锌镍合金镀层（含镍 12–15%）的三价铬彩色钝化，耐热性好；可配合有机封闭剂进一步提升耐蚀，同时保持原色。"),
    ("DF-120", "pas", "镀锌封闭剂",
     "Lớp phủ bảo vệ hậu xử lý sau thụ động với khả năng chống ăn mòn vượt trội và ít hao hụt khi gia nhiệt; sử dụng như bước bịt kín cuối cùng sau thụ động xanh hoặc trắng.",
     "Post-treatment coating after passivation with outstanding corrosion resistance and little loss on heating; used as the final sealing step after blue or clear passivation.",
     "钝化后的封闭涂层，耐蚀性卓越，受热损失小；用于蓝白或白色钝化后的最终封闭工序。"),
]


def _fill_blank(obj, values: dict) -> None:
    """Chi ghi vao o con trong - khong de len noi dung nguoi dung da sua."""
    for key, value in values.items():
        if getattr(obj, key) in (None, ""):
            setattr(obj, key, value)


def seed_website_content(db: Session) -> list[str]:
    """Dien noi dung website con thieu. Khong commit; tra ve cac ma vua duoc dua len web."""
    choose_groups = not db.query(common_models.CompanyProduct).filter(
        common_models.CompanyProduct.web_group.isnot(None)
    ).first()

    published = []
    for code, group, name_zh, desc_vi, desc_en, desc_zh in WEB_PRODUCTS:
        product = db.query(common_models.CompanyProduct).filter_by(code=code).first()
        if not product:   # ma bi bo khoi danh muc
            continue
        _fill_blank(product, {
            "name_zh": name_zh,
            "description": desc_vi,
            "description_en": desc_en,
            "description_zh": desc_zh,
        })
        if choose_groups:
            product.web_group = group
            published.append(code)
    return published


def seed_website(engine: Engine) -> None:
    with Session(engine) as db:
        seed_website_content(db)
        db.commit()


def main() -> None:
    from app.core.database import engine
    load_all_modules()
    with Session(engine) as db:
        published = seed_website_content(db)
        db.commit()
    print(f"Da dua {len(published)} ma len web." if published else "Da dien cac o con trong, khong doi ma nao tren web.")


if __name__ == "__main__":
    main()
