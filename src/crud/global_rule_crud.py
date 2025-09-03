from sqlalchemy.orm import Session
from typing import Optional, List
from src.schemas.global_rule import GlobalRuleCreate
from ..models import GlobalRule


def create_global_rule(db: Session, rule_data: GlobalRuleCreate) -> GlobalRule:
    rule_data_dict = rule_data.model_dump(exclude_unset=True)
    new_rule = GlobalRule(**rule_data_dict)

    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)

    return new_rule


def create_global_rules_batch(db: Session, rules: List[GlobalRuleCreate]) -> None:
    rule_dict_list = [r.model_dump(exclude_unset=True) for r in rules]
    new_rules = [GlobalRule(**r_dict) for r_dict in rule_dict_list]

    db.add_all(new_rules)
    db.commit()


def get_global_rule_by_norm_desc(db: Session, norm_desc: str) -> Optional[GlobalRule]:
    return db.query(GlobalRule).filter(GlobalRule.norm_desc == norm_desc).one_or_none()
