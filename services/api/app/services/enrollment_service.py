from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import EnrollToken, OrgMembership, Organization, UserProfile
from app.models.user import LearnerUser, User


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db

    def create_enroll_token(
        self,
        organization_id: int,
        expires_in_minutes: int = 24 * 60,
    ) -> tuple[str, EnrollToken]:
        raw_token = secrets.token_urlsafe(16)
        token_hash = self._hash(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)

        enroll_token = EnrollToken(
            organization_id=organization_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(enroll_token)
        self.db.flush()
        return raw_token, enroll_token

    def consume_token(self, token: str, user: User) -> Organization:
        token_hash = self._hash(token)
        now = datetime.now(timezone.utc)
        stmt = (
            select(EnrollToken)
            .where(EnrollToken.token_hash == token_hash)
            .where(EnrollToken.expires_at >= now)
            .limit(1)
        )
        enroll_token = self.db.scalar(stmt)
        if not enroll_token or enroll_token.used_by_user_id is not None:
            raise ValueError("Invalid or already used token.")

        organization = enroll_token.organization
        if organization is None:
            raise ValueError("Organization not found for token.")
        if organization.status != "active":
            raise ValueError("Organization is currently disabled.")

        membership_stmt = (
            select(OrgMembership)
            .where(OrgMembership.organization_id == organization.id)
            .where(OrgMembership.user_id == user.id)
            .limit(1)
        )
        membership = self.db.scalar(membership_stmt)

        if membership is None:
            membership = OrgMembership(
                organization_id=organization.id,
                user_id=user.id,
                org_role="member",
                status="active",
            )
            self.db.add(membership)
        else:
            membership.status = "active"

        user.organization_id = organization.id
        user.account_type = "organization_member"
        enroll_token.used_by_user_id = user.id

        learner_account = user.learner_account
        if learner_account is None:
            learner_account = LearnerUser(user_id=user.id, primary_org_id=organization.id)
            self.db.add(learner_account)
        else:
            learner_account.primary_org_id = organization.id

        profile = user.profile
        if profile is None:
            profile = UserProfile(user_id=user.id)
            self.db.add(profile)
        if not profile.student_id:
            profile.student_id = self._generate_student_id(organization)

        self.db.flush()
        return organization

    def _hash(self, token: str) -> str:
        payload = token.encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _generate_student_id(self, organization: Organization) -> str:
        prefix = organization.slug[:8].upper()
        while True:
            candidate = f"{prefix}-{secrets.token_hex(4)}"
            exists_stmt = select(UserProfile).where(UserProfile.student_id == candidate).limit(1)
            if self.db.scalar(exists_stmt) is None:
                return candidate
