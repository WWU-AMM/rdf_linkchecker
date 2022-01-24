from rdf_linkchecker.graph import get_urls


def test_combined(ttl_files, data_regression):
    urls = list(sorted(get_urls(ttl_files)))
    data_regression.check({"urls": urls})
