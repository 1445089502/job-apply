"""SQLAlchemy 模型（MVP 核心表）。"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.db import Base


class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    industry = Column(String(64), default="")
    city = Column(String(32), default="")
    scale = Column(String(32), default="")


class Job(Base):
    __tablename__ = "job"
    __table_args__ = (UniqueConstraint("platform", "job_id", name="uk_platform_job"),)

    id = Column(Integer, primary_key=True)
    platform = Column(String(16), nullable=False)
    job_id = Column(String(64), nullable=False)
    company_id = Column(Integer, ForeignKey("company.id"))
    title = Column(String(128), nullable=False)
    jd_text = Column(Text, nullable=False)
    city = Column(String(32), default="")
    salary_min = Column(Integer, default=0)  # 千/月
    salary_max = Column(Integer, default=0)
    experience_req = Column(String(32), default="")
    education_req = Column(String(32), default="")
    language_req = Column(String(64), default="")
    skills_json = Column(Text, default="[]")
    embedding = Column(Text, default="[]")  # JSON 向量
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company")


class UserPreference(Base):
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1, unique=True)
    resume_text = Column(Text, default="")
    preference_text = Column(Text, default="")
    behavior_embedding = Column(Text, default="[]")  # 行为学习向量
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserJobFeedback(Base):
    __tablename__ = "user_job_feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    action = Column(String(32), nullable=False)  # view/collect/apply/dislike
    weight = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class JobApplication(Base):
    __tablename__ = "job_application"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    status = Column(String(16), nullable=False, default="CREATED")
    resume_id = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MatchScore(Base):
    __tablename__ = "match_score"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, default=1)
    job_id = Column(Integer, ForeignKey("job.id"), nullable=False)
    hard_score = Column(Float, default=0.0)
    vec_score = Column(Float, default=0.0)
    final_score = Column(Float, default=0.0)
    reasons_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)
