#Owner::ANIKET::ANHOTRA = MR.Panda
"""Sites are scoped through the parent project and tenant membership."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.database import get_database_session
from backend.app.dependencies import get_current_user, require_project_membership
from backend.app.models.site_model import Site
from backend.app.models.user_model import User
from backend.app.schemas.site_schema import SiteCreate, SiteResponse
from backend.app.services.audit_service import record_audit

router = APIRouter(prefix="/projects/{project_id}/sites", tags=["sites"])
SITE_EDITOR_ROLES = frozenset({"owner", "project_manager", "site_engineer"})


@router.post("", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
def create_site(
    project_id: str,
    request: SiteCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> SiteResponse:
    """Add a physical site only with a verified engineering/manager role."""
    project = require_project_membership(session, user.id, project_id, SITE_EDITOR_ROLES)
    site = Site(project_id=project.id, **request.model_dump())
    session.add(site)
    session.flush()
    record_audit(
        session,
        actor_user_id=user.id,
        organization_id=project.organization_id,
        action="site.created",
        target_type="site",
        target_id=site.id,
        value_after={"name": site.name, "project_id": project.id},
    )
    session.commit()
    return SiteResponse.model_validate(site)


@router.get("", response_model=list[SiteResponse])
def list_sites(
    project_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_database_session),
) -> list[SiteResponse]:
    """Return project sites only after checking membership in its tenant."""
    require_project_membership(session, user.id, project_id)
    sites = session.scalars(
        select(Site).where(Site.project_id == project_id).order_by(Site.name, Site.id)
    ).all()
    return [SiteResponse.model_validate(site) for site in sites]
