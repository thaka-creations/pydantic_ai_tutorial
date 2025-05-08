from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(Integer, primary_key=True)
    exam_name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    question_number = Column(String, nullable=False)
    part_label = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    marks = Column(Integer)
    created_at = Column(TIMESTAMP, default=func.now())
