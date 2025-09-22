from collections.abc import Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.product_order import ProductOrder
from app.schemas.product_order import (
    ProductOrderCreate,
    ProductOrderRead,
    ProductOrderUpdate,
)


def create_order(db: Session, order_in: ProductOrderCreate) -> ProductOrder:
    order = ProductOrder(**order_in.model_dump())
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def get_order(db: Session, order_id: int) -> ProductOrder | None:
    return db.query(ProductOrder).filter(ProductOrder.id == order_id).first()


def get_order_by_number(db: Session, order_number: str) -> ProductOrder | None:
    return (
        db.query(ProductOrder)
        .filter(ProductOrder.order_number == order_number)
        .first()
    )


def list_orders(db: Session, skip: int = 0, limit: int = 50) -> Sequence[ProductOrder]:
    return db.query(ProductOrder).offset(skip).limit(limit).all()


def update_order(
    db: Session, order: ProductOrder, order_in: ProductOrderUpdate
) -> ProductOrder:
    payload = order_in.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in payload.items():
        setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


def delete_order(db: Session, order: ProductOrder) -> None:
    db.delete(order)
    db.commit()


def fetch_complex_class_payload(db: Session, class_seq: int) -> list[dict[str, object]]:
    """Execute a complex raw SQL example that joins many tables."""

    sql = text(
        """
        SELECT c.classSeq '클래스번호',
               c.className '클래스명',
               STUFF((SELECT ',' + ha.hashTagName
                      FROM HASHTAG ha
                               JOIN yanadoo_master..HASHTAG_RELATION hr
                                    ON hr.typeCode = 'CLASS'
                                        AND hr.relationSeq = c.classSeq
                                        AND ha.hashTagSeq = hr.hashTagSeq
                      FOR XML PATH('')), 1, 1, '') AS '클래스 해시태그 목록',
               comm.communitySeq '커뮤니티 번호',
               comm.title '커뮤니티명',
               l.lectureSeq '강의 번호',
               l.title '강의명',
               cp.seq '강의 CP사 번호',
               cp.name '강의 CP사명',
               STUFF((SELECT ',' + t.teacherName
                      FROM LECTURE_TO_TEACHER ltt
                               join yanadoo_master..TEACHER t on l.lectureSeq = ltt.lectureSeq and  (ltt.teacherSeq = t.teacherSeq)
                      FOR XML PATH('')), 1, 1, '') AS '강의 강사명 목록',
               am.assetMediaSeq '강의 미디어 번호',
               kmi.mediaContentKey '강의 미디어 컨텐츠 키',
               at.assetTrainingSeq '강의 트레이닝 번호',
               at.assetTrainingFileName '강의 트레이닝 파일명',
               att.assetTutorSeq 'AI 오드리 강의 튜터 번호',
               att.assetTutorFileName 'AI 오드리 강의 튜터 파일명',
               ae.assetExpressionSeq '강의 핵심표현 번호',
               kmi2.mediaContentKey '강의 핵심표현 미디어 컨텐츠 키',
               mi.missionSeq '강의 미션 번호',
               mi.missionName '강의 미션 명',
               laf.seq '강의 첨부파일 번호',
               laf.attachFileName '강의 첨부파일명'
        FROM yanadoo_master..CLASS c
                 left join yanadoo_master..CLASS_TO_COMMUNITY ctco on c.classSeq = ctco.classSeq
                 left join yanadoo_master..COMMUNITY_V2 comm on ctco.communitySeq = comm.communitySeq
                 join yanadoo_master..CLASS_TO_COURSE ctc on (c.classSeq = ctc.classSeq)
                 join yanadoo_master..COURSE co on (ctc.courseSeq = co.courseSeq)
                 join yanadoo_master..COURSE_TO_LECTURE ctl on (ctc.courseSeq = ctl.courseSeq)
                 join yanadoo_master..LECTURE l on (ctl.lectureSeq = l.lectureSeq)
                 left join yanadoo_master..CONTENT_PROVIDER cp on (l.contentProviderSeq = cp.seq)
                 join yanadoo_master..LECTURE_TO_ASSET lta on (l.lectureSeq = lta.lectureSeq)
                 left join yanadoo_master..ASSET_MEDIA am on (lta.relationSeq = am.assetMediaSeq and lta.assetType = 'MEDIA')
                 left join yanadoo_master..KOLLUS_MEDIA_INFO kmi on (am.uploadFileKey = kmi.uploadFileKey)
                 left join yanadoo_master..LECTURE_ATTACH_FILE laf on l.lectureSeq = laf.lectureSeq
                 left join yanadoo_master..ASSET_TRAINING at
                           on (lta.relationSeq = at.assetTrainingSeq and lta.assetType = 'TRAINING')
                 left join yanadoo_master..ASSET_TUTOR att on (l.lectureSeq = att.lectureSeq)
                 left join yanadoo_master..ASSET_EXPRESSION ae
                           on (lta.relationSeq = ae.assetExpressionSeq and lta.assetType = 'EXPRESSION')
                 left join yanadoo_master..KOLLUS_MEDIA_INFO kmi2 on (ae.uploadFileKey = kmi2.uploadFileKey)
                 left join yanadoo_master..MISSION mi on lta.relationSeq = mi.missionSeq and lta.assetType='MISSION'
        WHERE c.classSeq = :class_seq
        """
    )

    # NOTE: 이 SQL은 외부 스키마를 참조하므로 실제 실행 환경에 따라 실패할 수 있습니다.
    result = db.execute(sql, {"class_seq": class_seq}).mappings().all()
    return [dict(row) for row in result]
