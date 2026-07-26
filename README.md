Template adapted from [Jon Barron's website](https://jonbarron.info/) and [Yunzhi Zhang's website](https://ai.stanford.edu/~yzzhang/).

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
