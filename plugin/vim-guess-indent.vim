" vim-guess-indent.vim
"
"       Guess values for 'shiftwidth' and 'expandtab' automatically
"

if exists('g:vim_guess_indent_loaded') || v:version < 703 || &compatible
  finish
endif
let g:vim_guess_indent_loaded = 1

augroup GuessIndent_DetectAfterFileType
  autocmd!
  autocmd BufWritePost,FileType * call GuessIndent()
augroup END

let s:dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

function! GuessIndent()
  if &filetype == '' || &filetype == 'help'
    return
  endif
  " Need to override some options when I want to
  let program = s:dir . '/simple-guess.py'
  let filename = expand('%')
  let result = system('2>/dev/null ' . program . ' ' .  shellescape(filename))
  let translator =
        \{ '0': function('GuessIndent_do_nothing')
        \, '1': function('GuessIndent_do_tab_indent')
        \, '2': function('GuessIndent_do_space_indent')
        \, '3': function('GuessIndent_do_space_indent')
        \, '4': function('GuessIndent_do_space_indent')
        \, '8': function('GuessIndent_do_space_indent')
        \}
  if -1 != index(['0','1','2','3','4','8'], result)
    call translator[result](result)
  else
    call GuessIndent_do_nothing()
  endif
endfunction

function! GuessIndent_do_nothing(...)
  call GuessIndent_log('-')
endfunction

function! GuessIndent_do_tab_indent(...)
  call GuessIndent_log('TAB')
  execute 'setlocal noexpandtab'
endfunction

function! GuessIndent_do_space_indent(indent_step)
  call GuessIndent_log(a:indent_step . '-space')
  execute 'setlocal expandtab'
  execute 'setlocal shiftwidth=' . a:indent_step
  execute 'setlocal softtabstop=' . a:indent_step
endfunction

function! GuessIndent_log(message)
  " Maybe add the guesser status to status line or status bar
  let b:vim_guess_indent_log = a:message
endfunction

function! GuessIndent_get_log()
  return exists('b:vim_guess_indent_log') ? b:vim_guess_indent_log : ''
endfunction

" TODO: FIXME: Side effect
set statusline=%<%f\ %h%m%r%=%{GuessIndent_get_log()}
