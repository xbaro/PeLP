from typing import Optional
from django.db.models import Count
from pelp.apps.web.models import Faq, FaqTag, TranslateFaqTag


def get_tag_histogram(include_private=False):
    query = FaqTag.objects
    if not include_private:
        query = query.filter(faq__public=True)
    hist = query.annotate(
        num=Count('faq')
    ).values_list('tag', 'num', 'tag')

    multilang_hist = []
    for tag in hist:
        info = { l[0]: l[1] for l in TranslateFaqTag.objects.filter(faqtag__tag=tag[0]).values_list('language', 'tag')}
        multilang_hist.append([tag[0], tag[1], info])

    return multilang_hist

