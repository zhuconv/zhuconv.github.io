Template adapted from [Jon Barron's website](https://jonbarron.info/) and [Yunzhi Zhang's website](https://ai.stanford.edu/~yzzhang/).

## Personal portal

Visit [the portal](https://zhuconv.github.io/portal/) for the site's pages and
redirect links. Every push to `main` runs the GitHub Pages workflow, builds the
site, and regenerates the portal from all published `.html` and `.htm` files.
Adding or deleting a page automatically updates the directory. The portal itself
and assets such as PDFs, images, CSS, and JavaScript are not listed.

Redirects are detected from their `<meta http-equiv="refresh">` tags, so changing
a redirect's URL also updates the portal. Titles come from each page's `<title>`;
an optional `<meta name="portal-title" content="Book a chat">` overrides the label.
There is no separate URL list to maintain. Copy buttons share the public short
URLs, and the portal remains marked `noindex`.

GitHub Pages uses **GitHub Actions** as its publishing source. The workflow runs
the existing Jekyll build, then `python3 scripts/generate-portal.py --site _site`
before uploading the site. `portal/index.html` is the layout template; its two
marked directory sections are filled in the build output. To preview a built
site, run `python3 -m http.server --directory _site`. Run the discovery checks with
`python3 -m unittest discover -s tests -v`.

## Paper images

Paper figures can be kept as single-page PDFs in `images/papers`. Generate the
same-name PNG previews with:

```sh
brew install poppler
make paper-images
```

The converter renders each figure with a maximum 1600px edge, then rejects any
PNG over 1 MiB. Run `make check-paper-images` to validate existing outputs
without changing them.
