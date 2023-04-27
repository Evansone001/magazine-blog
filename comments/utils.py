import logging

from djangoblog.utils import get_current_site
from djangoblog.utils import send_email

logger = logging.getLogger(__name__)


def send_comment_email(comment):
    site = get_current_site().domain
    subject = 'Thank you for your published Comment'
    article_url = "https://{site}{path}".format(
        site=site, path=comment.article.get_absolute_url())
    html_content = """
                   <p>Thank you very much for publishingComment on this site</p>
                   You can visit
                   <a href="%s" rel="bookmark">%s</a>
                   to view your Comment，
                   Thank you again！
                   <br />
                   If the link above does not work, please copy this link to your browser。
                   %s
                   """ % (article_url, comment.article.title, article_url)
    tomail = comment.author.email
    send_email([tomail], subject, html_content)
    try:
        if comment.parent_comment:
            html_content = """
                    you are <a href="%s" rel="bookmark">%s</a> Comment <br/> %s <br/> I received a reply. Go check it out
                    <br/>
                    If the link above does not work, please copy this link to your browser。
                    %s
                    """ % (article_url, comment.article.title, comment.parent_comment.body, article_url)
            tomail = comment.parent_comment.author.email
            send_email([tomail], subject, html_content)
    except Exception as e:
        logger.error(e)
