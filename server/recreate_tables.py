#!/usr/bin/env python3
# server/recreate_tables.py
"""
Drop and recreate all tables.
"""
from db.database import engine, Base
from models import Job, JobChunk, InterviewSession, InterviewResult, Question, PersonaDB, Company, Applicant

print("Dropping all tables...")
Base.metadata.drop_all(bind=engine)
print("✓ All tables dropped")

print("\nCreating all tables...")
Base.metadata.create_all(bind=engine)
print("✓ All tables created successfully")
