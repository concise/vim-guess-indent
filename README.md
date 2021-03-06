# vim-guess-indent

This is a Vim plugin that helps you determine which values of 'shiftwidth' and
'expandtab' should be used automatically when a text buffer is created based on
its content.


## Watch me code this project

1. [Episode 01](https://www.youtube.com/watch?v=F0gc05Jq1f0)


## Caveats

This plugin is still at alpha quality, and using it might break some parts of
your Vim.


## How to install

0. Manually

    Put the two files `simple-guess.py` and `vim-guess-indent.vim` into the
    `plugin/` directory within any directory of your `runtimepath`.

1. With pathogen

        cd ~/.vim/bundle/
        git clone https://github.com/concise/vim-guess-indent

2. With Vundle

        Plugin 'concise/vim-guess-indent'

3. With Neobundle

        NeoBundle 'concise/vim-guess-indent'

## TODO

This plugin has a side effect that it will modify the status bar to indicate
the result of its guess.

This plugin currently uses an external program (a Python script) to perform the
guess.  I'd like to refactor it into a pure VimL script to be faster.

I should add callback function hooks so that the user can define some function
that can change 'listchar' option based on which indentation should be used for
the current buffer.
