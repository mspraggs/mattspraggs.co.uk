from pelican import contents, signals
from pelican.generators import ArticlesGenerator


def fix_heading_tags(instance):
    """
    Increase level of all heading tags in content by two.

    Once this function is applied to an article, heading tags will start from
    <h3>.

    :param instance: Content instance.
    :return:
    """

    if not isinstance(instance, contents.Article):
        return

    content = instance._content
    for i in range(10, 0, -1):
        content = content.replace(f'<h{i}>', f'<h{i+2}>')
        content = content.replace(f'</h{i}>', f'</h{i+2}>')

    instance._content = content


def run_plugin(generator):
    if isinstance(generator, ArticlesGenerator):
        for article in generator.articles:
            fix_heading_tags(article)


def register():
    try:
        signals.article_generator_finalized.connect(run_plugin)
    except AttributeError:
        # NOTE: This may result in #314 so shouldn't really be relied on
        # https://github.com/getpelican/pelican-plugins/issues/314
        signals.content_object_init.connect(fix_heading_tags)
