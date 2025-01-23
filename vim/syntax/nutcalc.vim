" Vim syntax file
" Language: Nutcalc
" Maintainer: Jacob Thomas Errington
" Latest Revision: January 2025

if exists("b:current_syntax")
    finish
endif

syntax clear

syntax match nutComment '#.*' contains=NONE
highlight link nutComment Comment

syntax keyword nutCoreKeywords import weighs
highlight link nutCoreKeywords Keyword

syntax keyword nutWeightKeywords g kg mg oz lb
highlight link nutWeightKeywords Type

syntax match nutSpecial '[:=-]'
highlight link nutSpecial Special

syntax match nutOperator '[+*/]'
highlight link nutOperator Operator

syntax match nutNumber '\d\+\(\.\d\+\)\?' skipwhite nextgroup=nutUnit
highlight link nutNumber Number

syntax match nutUnit '\<[a-zA-Z][0-9a-zA-Z]*\>\|\'[^\']\'\|"[^"]"\>' skipwhite nextgroup=nutIdent
highlight link nutUnit Type

syntax region nutUnit start=/"/ end=/"/
syntax region nutUnit start=/'/ end=/'/
syntax region nutIdent start=/"/ end=/"/
syntax region nutIdent start=/'/ end=/'/

syntax match nutIdent '\<[a-zA-Z][0-9a-zA-Z]*\>\|\'[^\']\'\|"[^"]"'
highlight link nutIdent Identifier
