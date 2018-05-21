"""
    View helpers
"""

def is_ready(work):
    must_have = [
        'subscription',
        'modality',
        'area_category',
        'title',
        'summary',
        'keywords',
        'accepts_terms',
    ]

    if work.modality == 'artigo':
        if 'banner_file' in must_have:
            must_have.remove('banner')
        must_have.append('article_file')
    elif work.modality == 'banner':
        if 'article_file' in must_have:
            must_have.remove('article_file')
        must_have.append('banner_file')
    elif work.modality == 'resumo':
        if 'article_file' in must_have:
            must_have.remove('article_file')

        if 'banner_file' in must_have:
            must_have.remove('banner')

    for item in must_have:
        if not getattr(work, item) or work.authors.all().count() < 1:
            return False

    return True

