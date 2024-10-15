dylan's citation.nvim
============

**Personal plugin for dylan's phd.**

You likely can't use this, as it expects expects a specific zotero setup and bibtex file.
If you are really interested read through my [.dots](http://github.com/dmadisetti/.dots)
and [phd](http://github.com/dmadisetti/phd). if that still hasn't dissuaded you,
and you remain interested, give me an email- i guess.

---

[citation.vim](https://github.com/rafaqz/citation.vim) rewritten for [denite.nvim](https://github.com/Shougo/denite.nvim) and my workflow.


### Installation

1. Install [denite.nvim](https://github.com/Shougo/denite.nvim)
2. Install this plugin in vim however you like to do that.
3. Choose your source

    Only works with pybtex

    * install [pybtex](http://pypi.python.org/pypi/pybtex)

      ``` bash
      easy_install pybtex
      ```

    * Set variables:

      ```vimscript
      let g:citation_vim_bibtex_file="/path/to/your/bib/file/library.bib"
      let g:citation_vim_mode="bibtex"

      ```

4. Set a cache path:

  ```vimscript
  let g:citation_vim_cache_path='~/.vim/your_cache_path'
  ```

5. Set the et al. limit. If the number of authors is greater than the limit only
   the first author with `et al.` appended is shown or printed in case of
   `citation/author`. (Default: 5)

  ```vimscript
  let g:citation_vim_et_al_limit=2
  ```

6. The default order results are displayed in was recently reversed so your
  recent additions are allways at the top. If you want to keep the old
  behaviour, set:

  ```vimscript
  let g:citation_vim_reverse_order=0
  ```

7. Set some mappings. Copy and paste the following examples into your vimrc to get started.

### Key mappings:

```vimscript
" Example (see github:dmadisetti/.dots:dot/vim/config/plugins/denite.vim)
autocmd FileType denite call s:denite_my_settings()
function! s:denite_my_settings() abort
  nnoremap <silent><buffer><expr> q denite#do_map('quit')
  nnoremap <silent><buffer><expr>  <CR>     denite#do_map('do_action')
  nnoremap <silent><buffer><expr>  <Space>  denite#do_map('toggle_select').'j'
  nnoremap <silent><buffer><expr>  a        denite#do_map('choose_action')
  nnoremap <silent><buffer><expr>  d        denite#do_map('do_action', 'delete')
  nnoremap <silent><buffer><expr>  p        denite#do_map('do_action', 'preview')
  nnoremap <silent><buffer><expr>  o        denite#do_map('do_action', 'open')
  nnoremap <silent><buffer><expr>  i        denite#do_map('open_filter_buffer')
  nnoremap <silent><buffer><expr>  <Esc>    denite#do_map('quit')
endfunction

nnoremap <C-q> :Denite -buffer-name=citation-start-insert  -vertical-preview citation_collection<cr>
inoremap <C-q> <C-c>:Denite -buffer-name=citation-start-insert  -vertical-preview citation_collection<cr>
```

### Tweaks

Customise the unite display, using the names of citation sources and a python
format string (the {} braces will be replaced by the sources):

```vimscript
let g:citation_vim_description_format = "{}∶ {} \˝{}\˝ ₋{}₋ ₍{}₎"
let g:citation_vim_description_fields = ["key", "author", "doi", "journal", "whateveryouwant"]
```

You might have noticed the weird characters in the description format string.
They are used for highlighting sections, to avoid confusion with
normal characters that might be in the citation.

To change description highlighting characters, copy and paste characters from this list:
- Quotes                  ″‴‶‷
- Brackets                ⊂〔₍⁽     ⊃〕₎⁾
- Arrows                  ◀◁<‹    ▶▷>›
- Blobs                   ♯♡◆◇◊○◎●◐◑∗∙⊙⊚⌂★☺☻▪■□▢▣▤▥▦▧▨▩
- Tiny                    、。‸₊⁺∘♢☆☜☞♢☼
- Bars                    ‖│┃┆∥┇┊┋
- Dashes                  ‾⁻−₋‐⋯┄–—―∼┈─▭▬┉━┅₌⁼‗

- And use these like a colon after words (notice that's not a normal colon)
        ∶∷→⇒≫

Long lines will occasionally break the display colors. It's a quirk of how unite
shortens lines.


### Troubleshooting

You can correct your .bib file with `pybtex-convert`:

```sh
pybtex-convert /path/to/your.bib out.bib
```

If you have other problems, open an issue on github and include the error output
from vim. Please pull the latest changes first, and include your vim/nvim
version and zotero versions in the issue. Attaching your bib(la)tex file may also be
helpful if using the bibtex/biblatex backend.

