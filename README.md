# vim-guess-indent

This is a Vim plugin that helps you determine which values of 'shiftwidth' and
'expandtab' should be used automatically when a text buffer is created based on
its content.



## How to install

0. Manually

Put the two files `simple-guess.py` and `vim-guess-indent.vim` into any one
`plugin/` directory withing your runtimepaths.

1. With pathogen

    git clone https://github.com/concise/vim-guess-indent ~/.vim/bundle/vim-guess-indent

2. With Vundle

    Plugin 'concise/vim-guess-indent'

3. With Neobundle

    NeoBundle 'concise/vim-guess-indent'



## Notes

This plugin has a side effect that it will modify the status bar to indicate
the result of its guess.

This plugin currently use an external program (a Python script) to perform the
guess.  I'd like to refactor it into a pure VimL script.
