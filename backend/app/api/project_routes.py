#Owner::ANIKET::ANHOTRA = MR.Panda
"""Organisation-scoped construction project create and list endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_database_session
from backend.app.dependencies import (
    get_current_user,
    require_organization_membership,
    require_project_membership,
)
from backend.app.models.membership_model import Membership
from backend.app.models.project_model import Project
from backend.app.models.user_model import User
from backend.app.schemas.project_schema import ProjectCreate, ProjectResponse
from backend.app.services.audit_service import record_audit

router = APIRouter(prefix="/projects", tags=["projects"])
PROJECT_EDITOR_ROLES = frozenset({"owner", "project_manager"})


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    request: ProjectCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> ProjectResponse:
    """Create a project only if the current tenant role permits it."""
    require_organization_membership(
        session, user.id, request.organization_id, PROJECT_EDITOR_ROLES
    )
    project = Project(**request.model_dump())
    session.add(project)
    session.flush()
    record_audit(
        session,
        actor_user_id=user.id,
        organization_id=project.organization_id,
        action="project.created",
        target_type="project",
        target_id=project.id,
        value_after={"name": project.name},
    )
    session.commit()
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> list[ProjectResponse]:
    """List only projects attached to a current organisation membership."""
    projects = session.scalars(
        select(Project)
        .join(Membership, Membership.organization_id == Project.organization_id)
        .where(Membership.user_id == user.id)
        .order_by(Project.created_at, Project.id)
    ).all()
    return [ProjectResponse.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> ProjectResponse:
    """Read a project only if its organisation is accessible to the caller."""
    project = require_project_membership(session, user.id, project_id)
    return ProjectResponse.model_validate(project)
