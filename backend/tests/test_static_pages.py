"""Tests for default static page backfills."""

from app.models.cms import StaticPageContent
from app.static_pages import ensure_default_static_pages


class FakeEditor:
    id = 1


def test_ensure_default_static_pages_creates_missing_page(db_session):
    editor = FakeEditor()

    created = ensure_default_static_pages(
        db_session,
        editor=editor,
        slugs=["staffer-application"],
    )

    page = (
        db_session.query(StaticPageContent)
        .filter(StaticPageContent.page_slug == "staffer-application")
        .one()
    )
    assert created == 1
    assert page.title == "Applying to be a Senate Staffer"
    assert page.last_edited_by == editor.id


def test_ensure_default_static_pages_does_not_overwrite_existing_page(db_session):
    editor = FakeEditor()
    db_session.add(
        StaticPageContent(
            page_slug="staffer-application",
            title="Custom Staffer Page",
            body="<p>Custom content</p>",
            last_edited_by=editor.id,
        )
    )
    db_session.flush()

    created = ensure_default_static_pages(
        db_session,
        editor=editor,
        slugs=["staffer-application"],
    )

    page = (
        db_session.query(StaticPageContent)
        .filter(StaticPageContent.page_slug == "staffer-application")
        .one()
    )
    assert created == 0
    assert page.title == "Custom Staffer Page"
    assert page.body == "<p>Custom content</p>"


def test_ensure_default_static_pages_skips_without_editor(db_session):
    created = ensure_default_static_pages(db_session, slugs=["staffer-application"])

    assert created == 0
    assert db_session.query(StaticPageContent).count() == 0
