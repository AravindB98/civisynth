from civisynth.ingest import parse_rss

RSS_SAMPLE = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Politics Feed</title>
    <item>
      <title>Senate passes budget resolution</title>
      <link>https://example.com/budget</link>
      <description>&lt;p&gt;The senate passed the budget resolution late Thursday.&lt;/p&gt;</description>
      <pubDate>Thu, 09 Jul 2026 22:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Governor signs energy bill</title>
      <link>https://example.com/energy</link>
      <description>The governor signed the energy bill today.</description>
      <pubDate>Fri, 10 Jul 2026 10:00:00 GMT</pubDate>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_extracts_documents():
    docs = parse_rss(RSS_SAMPLE, source="Example", leaning="center")
    assert len(docs) == 2
    assert docs[0].title == "Senate passes budget resolution"
    assert "budget resolution" in docs[0].text
    assert "<p>" not in docs[0].text
    assert docs[0].source == "Example"
    assert docs[0].url == "https://example.com/budget"
    assert docs[0].published.year == 2026
    assert docs[0].id and docs[0].id != docs[1].id
