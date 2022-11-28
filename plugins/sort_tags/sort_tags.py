from operator import itemgetter
from pelican import signals


def sort_tags_by_frequency(generator):
    tags = sorted(
        generator.tags.items(),
        key=_extract_and_size,
        reverse=False,
    )
    generator.context['tags_sorted_by_frequency'] = tags


def register():
    signals.article_generator_finalized.connect(sort_tags_by_frequency)


def _extract_and_size(item):
    articles = itemgetter(1)(item)
    length = len(articles)
    tag_lower = (itemgetter(0)(item)).slug.lower()
    return -length, tag_lower