"""Email digest service using Resend."""

import hashlib
import hmac
import logging
from typing import Optional
from uuid import UUID

from app.config import settings

logger = logging.getLogger(__name__)


def generate_feedback_url(user_id: UUID, paper_id: UUID, action: str) -> str:
    """Generate a signed feedback URL for email click tracking."""
    payload = f"{user_id}:{paper_id}:{action}"
    signature = hmac.new(
        settings.feedback_secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return f"{settings.app_url}/api/feedback?u={user_id}&p={paper_id}&a={action}&sig={signature}"


def verify_feedback_signature(user_id: str, paper_id: str, action: str, signature: str) -> bool:
    """Verify a feedback URL signature."""
    payload = f"{user_id}:{paper_id}:{action}"
    expected = hmac.new(
        settings.feedback_secret.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:16]
    return hmac.compare_digest(expected, signature)


def render_digest_html(papers: list[dict], user_id: UUID) -> str:
    """Render the daily digest email HTML."""
    paper_rows = ""
    for i, paper in enumerate(papers, 1):
        title = _escape_html(paper.get("title", "Untitled"))
        abstract = _escape_html(paper.get("abstract", "")[:200])
        if paper.get("abstract") and len(paper["abstract"]) > 200:
            abstract += "..."
        authors = ", ".join(
            a.get("name", "") for a in (paper.get("authors") or [])[:3]
        )
        if len(paper.get("authors") or []) > 3:
            authors += " et al."

        paper_id = paper.get("id", "")
        save_url = generate_feedback_url(user_id, paper_id, "save")
        skip_url = generate_feedback_url(user_id, paper_id, "skip")
        view_url = f"{settings.app_url}/paper/{paper_id}"

        paper_rows += f"""
        <tr>
          <td style="padding: 16px 0; border-bottom: 1px solid #e5e7eb;">
            <h3 style="margin: 0 0 4px 0; font-size: 16px; color: #111827;">
              <a href="{view_url}" style="color: #2563eb; text-decoration: none;">{i}. {title}</a>
            </h3>
            <p style="margin: 0 0 8px 0; font-size: 13px; color: #6b7280;">{authors}</p>
            <p style="margin: 0 0 8px 0; font-size: 14px; color: #374151;">{abstract}</p>
            <div>
              <a href="{save_url}" style="display: inline-block; padding: 4px 12px; background: #2563eb; color: white; border-radius: 4px; text-decoration: none; font-size: 13px; margin-right: 8px;">Save</a>
              <a href="{skip_url}" style="display: inline-block; padding: 4px 12px; background: #f3f4f6; color: #374151; border-radius: 4px; text-decoration: none; font-size: 13px;">Skip</a>
            </div>
          </td>
        </tr>
        """

    if not paper_rows:
        paper_rows = """
        <tr><td style="padding: 20px; text-align: center; color: #6b7280;">
          No new papers matched your interests today. Check back tomorrow!
        </td></tr>
        """

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f9fafb;">
  <div style="background: white; border-radius: 8px; padding: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
    <h1 style="font-size: 24px; color: #111827; margin: 0 0 4px 0;">Research Radar</h1>
    <p style="color: #6b7280; margin: 0 0 20px 0; font-size: 14px;">Your daily paper digest</p>
    <table style="width: 100%; border-collapse: collapse;">
      {paper_rows}
    </table>
    <p style="margin-top: 20px; font-size: 12px; color: #9ca3af; text-align: center;">
      <a href="{settings.app_url}/settings" style="color: #6b7280;">Manage preferences</a> ·
      <a href="{settings.app_url}/feed" style="color: #6b7280;">View feed</a>
    </p>
  </div>
</body>
</html>"""


async def send_digest_email(
    to_email: str,
    papers: list[dict],
    user_id: UUID,
) -> bool:
    """Send a digest email via Resend."""
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured, skipping email send")
        return False

    html = render_digest_html(papers, user_id)

    try:
        import resend
        resend.api_key = settings.resend_api_key

        result = resend.Emails.send({
            "from": settings.email_from,
            "to": [to_email],
            "subject": f"Research Radar: {len(papers)} papers for you",
            "html": html,
        })
        logger.info(f"Digest email sent to {to_email}: {result}")
        return True
    except Exception as e:
        logger.error(f"Failed to send digest email to {to_email}: {e}")
        return False


def _escape_html(text: str) -> str:
    """Basic HTML escaping."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
