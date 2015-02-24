function! s:before_guess_hook()
endfunction

function! s:after_guess_hook()
endfunction

let s:default_options = {
      \'before_guess_hook': function('s:before_guess_hook'),
      \'after_guess_hook': function('s:after_guess_hook')
      \}

function! s:get_option(key)
  if !has_key(s:default_options, a:key)
    throw 'KEY_NOT_FOUND'
  elseif !exists('g:guess_indent_options')
    return s:default_options[a:key]
  elseif type(g:guess_indent_options) != type({})
    return s:default_options[a:key]
  elseif !has_key(g:guess_indent_options, a:key)
    return s:default_options[a:key]
  elseif type(g:guess_indent_options[a:key]) != type(s:default_options[a:key])
    return s:default_options[a:key]
  else
    return g:guess_indent_options[a:key]
  endif
endfunction

let TEST = function('s:get_option')



augroup GuessIndent_DetectAfterFileType
  autocmd!
  autocmd BufWritePost,FileType * call GuessIndent()
augroup END

let s:dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

function! GuessIndent()
  if &filetype == '' || &filetype == 'help'
    call GuessIndent_do_nothing()
    return
  endif
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
  execute 'setlocal shiftwidth=' . &tabstop
  execute 'setlocal softtabstop=' . &tabstop
endfunction

function! GuessIndent_do_space_indent(indent_step)
  call GuessIndent_log(a:indent_step . '-space')
  execute 'setlocal expandtab'
  execute 'setlocal shiftwidth=' . a:indent_step
  execute 'setlocal softtabstop=' . a:indent_step
endfunction

function! GuessIndent_log(message)
  let b:guess_indent_log = a:message
endfunction

function! GuessIndent_get_log()
  return exists('b:guess_indent_log') ? b:guess_indent_log : '-'
endfunction



"
" Because I am lazy, I just change the "statusline" setting here.  This side
" effect should be removed in the future.  It would be nice to let it shows a
" notify message in the last line for just a few second.  Need to provide a
" way for the user to customize some callback hooks and options for this
" plugin.
"
set statusline=%<%f\ %h%m%r%=%{GuessIndent_get_log()}

"
" About the tab annoyance.  I should use "listchars" for only tab rendering,
" because Vim does not let me have local setting of "listchars" for each
" buffer or each window and the highlighting is not so customizable and sucks
" so much...  If "listchars" is actually used only for tab rendering, then
" here I only need to toggle "list" option, or keep "list" on and switch
" "listchars" between an empty string and a string value "tab:▸ ".
"
" On no, "listchars" is global.  So I cannot have two different buffer, one
" with Tab indentation and nother with space indentation, having different
" visualization of the tab characters while keep the "list" option on.
"
" Also, even when I use the Tab indentation, I would love to see those
" non-beginning-of-line tab characters...  Anyway I think ":se list lcs=>-"
" will work for most cases, though it is not that beautiful.
"

"
" For trailing-whitespace annoyance, I should come up with another mini plugin
" to handle that.  So does the more-than-80-column annoyance.
"

command! -nargs=? TAT call _listchars_value_without_tab()
function! _listchars_value_without_tab()
  let in = &listchars

  let tmplist = split(in, ',')
  call filter(tmplist, 'stridx(v:val,"tab")!=0')
  let out = join(tmplist, ',')

  return out
endfunction
