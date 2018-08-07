var defStyles = { // some repetitive innerHTML
    popWin: 'width: 70%; cursor: default; visibility: hidden; font-size: 80%; color: white;' + 
    'background-color: rgba(0,0,0,0.8);  text-align: center; position: absolute;' + 
    ' border: 2px solid gray; font-family: Amiri;',
    popCan: '<strong style="cursor: pointer;" class="fa fa-times pull-left fs-60"></strong>',
    popPlay: '<strong style="cursor: pointer;" class="fa fa-1x fa-play"></strong>',
    popPause: '<strong style="cursor: pointer;" class="fa text-danger fa-1x fa-stop"></strong>',
    popDrag: '<strong style="cursor: pointer;" class="fa fa-arrows pull-right fs-60"></strong>',
    popText: '<br><br><strong class="fa fa-refresh fa-spin"></strong>' // using loading icon waiting for translation
}

var defActions = { // some default repetitive events handlers
    toClicked: function (btn) {
        btn.onmousedown = function () { btn.classList.add('text-danger') }
        btn.onmouseup = function () { btn.classList.remove('text-danger') }
    },
    toLighten: function (btn, ovr) {
        btn.onmouseover = function () { ovr.style.backgroundColor = 'rgba(0,0,0,0.5)' }
        btn.onmouseleave = function () { ovr.style.backgroundColor = 'rgba(0,0,0,0.8)' }
    },
    toDarken: function (btn, ovr) {
        btn.onmouseover = function () { ovr.style.backgroundColor = 'rgba(0,0,0,1)' }
        btn.onmouseleave = function () { ovr.style.backgroundColor = 'rgba(0,0,0,0.8)' }
    },
    toCan: function (btn, ovr) {
        defActions.toLighten(btn, ovr)
        btn.onclick = function () {
            ovr.style.visibility = 'hidden'
        }
    },
    toDrag: function (btn, ovr) {
        defActions.toDarken(btn, ovr)
        $(ovr).draggable()
        $(ovr).draggable('disable')
        if (defControl.isMobile()) { // solving draggable touch on mobile
            btn.onclick = function () {
                if (btn.getAttribute('locked') === 'yes') {
                    btn.setAttribute('locked', 'no')
                    $(ovr).draggable('disable')
                    ovr.style.backgroundColor = 'rgba(0,0,0,0.8)'
                } else {
                    btn.setAttribute('locked', 'yes')
                    $(ovr).draggable('enable')
                    ovr.style.backgroundColor = 'rgba(0,0,0,1)'
                }
            }
        } else {
            btn.onmousedown = function () {
                $(ovr).draggable('enable')
                ovr.style.backgroundColor = 'rgba(0,0,0,1)'
            }
            btn.onmouseup = function () {
                $(ovr).draggable('disable')
                ovr.style.backgroundColor = 'rgba(0,0,0,0.8)'
            }
        }
    },
    toRead: function (curEle, theVal, theFunc) {
        fetch(
            window.location.origin + '/gtts/' +
            document.getElementById(theVal).value + 
            '/' + defControl.tagsFilter(curEle.innerText),
            {method: 'GET', credentials: 'include'}
        ).then(function (r) { return r.json() })
        .then(theFunc)
        .catch(function (e) {
            defControl.stopAll(true)
            showError()
            setTimeout(function () { 
                defControl.clearAll()
                tagReady()
             }, 3000)
        }) // if errors out
    },
    toTran: function (curEle, theVal, theFunc) {
        fetch(
            window.location.origin + '/tran/' +
            document.getElementById('readLang').value.split('-')[0] + '/' +
            document.getElementById(theVal).value +
            '/' + defControl.tagsFilter(curEle.innerText),
            {method: 'GET', credentials: 'include'}
        ).then(function (r) { return r.json() })
        .then(theFunc)
        .catch(function (e) {
            defControl.stopAll(true)
            showError()
            setTimeout(function () { 
                defControl.clearAll()
                tagReady()
             }, 3000)
        }) // if errors out
    }
}

var defControl = {
    // Some default media and elements control functions
    stop: function (aElement) { 
        if (aElement.duration) aElement.currentTime = aElement.duration
    },
    isPlaying: function (aElement) {
        return aElement ? aElement.currentTime !== aElement.duration : false
    },
    stopAll: function (all=false, aName='') {
        [ // to stop other aElements before playing aElement
            'beenPlayed', 'tranPlayed', 'beenPlayAll', 'beenTranAll'
        ].forEach(function (i){
            if (all && defControl.isPlaying(window[i])) defControl.stop(window[i])
            else if (i !== aName && defControl.isPlaying(window[i])) defControl.stop(window[i])
        })
    },
    playIt: function (aName, src, toEnd) {
        defControl.stopAll(false, aName)
        // to create audio and play it
        window[aName] = document.createElement('AUDIO')
        window[aName].src = window.location.origin + src
        window[aName].onended = toEnd
        window[aName].play()
    },
    fastF: function (aElement, fDur=(aElement.duration / 10)) {
        // to fast forward
        aElement.currentTime = (aElement.currentTime + fDur)  
    },
    fastB: function (aElement, fDur=(aElement.duration / 10)) {
        // to fast backward
        aElement.currentTime = (aElement.currentTime - fDur) 
    },
    clearAll: function () {
        // to clear all audio and popups
        ['beenPlayed', 'tranPlayed', 'beenPlayAll', 'beenTranAll', 'rOver']
        .forEach(function (i) {
            window[i] = undefined
        })
    },
    tagsFilter: function (text='') {
        // to filter text of html tags
        return text.replace(/<\/?[^>]+(>|$)/g, "")
    },
    currently_displayed: '', // work around to remove popup text from main div before read
    isMobile: function () { 
        // to detect if mobile device is used
        return (typeof window.orientation !== "undefined"
    ) || (navigator.userAgent.indexOf('IEMobile') !== -1) 
    }
}

var textTagger = function textTagger (element, splitters, ifIt, todo) {
    // DEFAULTS : (HTML_Element, [' ', ...], 'click,mouseover', ()=>{}, ()=>{} )
    // to split element content and return it wrapped with div tags and
    // onclick, onmouseover, onmouseleave ifIts
    var inner = window.storeOldText || element.innerHTML
    window.storeOldText = inner
    inner = inner.split(new RegExp("([" + splitters.join('') + "])"))
    inner.forEach(function (c, i) {
        if (splitters.indexOf(c) !== -1) {
            inner[i > 0 ? i - 1 : i] = inner[i > 0 ? i - 1 : i] + c
            inner.splice(i, 1)
        }
    })
    inner.splice(-1, 1)
    inner.map(function (content) {
        var nEle = document.createElement('div')
        var popper = document.createElement('div')
        var popText = document.createElement('span')
        var popPlay = document.createElement('span')
        var popCan = document.createElement('span')
        var popDrag = document.createElement('span')
        var par = document.createElement('p')
        nEle.style.display = 'inline'
        popper.style.cssText = popper.style.cssText + defStyles.popWin + 'z-index: 3;'
        popText.innerHTML = defStyles.popText
        popText.style.cursor = 'default'
        popCan.innerHTML = defStyles.popCan
        popDrag.innerHTML = defStyles.popDrag
        defActions.toDrag(popDrag, popper)
        defActions.toCan(popCan, popper)
        popPlay.innerHTML = defStyles.popPlay
        popPlay.onclick = function () {
            defControl.currently_diplayed = popText.innerText
            defActions.toRead(
                popText,
                'tranLang',
                function (j) {
                    if (defControl.isPlaying(window.tranPlayed)) defControl.stop(window.tranPlayed)
                    else {
                        popPlay.innerHTML = defStyles.popPause
                        defControl.playIt('tranPlayed', j.mp3, function () { popPlay.innerHTML = defStyles.popPlay })
                    }
                }
            )
        }
        par.innerHTML = content
        par.style.cssText = nEle.style.cssText + 'display: inline; padding: 0%; margin: 0% !important; cursor: pointer;'
        popper.appendChild(popCan)
        popper.appendChild(popPlay)
        popper.appendChild(popDrag)
        popper.appendChild(popText)
        nEle.appendChild(popper)
        nEle.appendChild(par)
        for (var toI = 0; par.children.length > toI; toI += 1) {
            par.children[toI].style.cssText = par.children[toI].style.cssText + 'padding: 0% !important;'
        }
        par.onclick = function () {
            if (ifIt.indexOf('click') !== -1) todo(par)
            defActions.toTran(par, 'tranLang', function (j) {
                popText.innerHTML = '<br><br>' + j.translation
                if (popper.style.visibility !== 'visible') popper.style.visibility = 'visible'
            })
        }
        par.onmouseover = function () {
            par.style.cssText = par.style.cssText + 'color: yellow !important;'
            if (ifIt.indexOf('mouseover') !== -1) todo(par)
        }
        par.onmouseout = function () {
            par.style.cssText = par.style.cssText + 'color: white !important;'
            if (ifIt.indexOf('mouseover') !== -1) defControl.stop(window.beenPlayed)
        }
        return nEle
    }).forEach(function (ele, i) {
        if (i === 0) element.innerHTML = ''
        element.appendChild(ele)
    })
    return element
}

var readTranAll = function (tagName='.splitIt', tran=false) {
    // to control gtts and translation of all tagName innerText
    var gn = function () { return tran ? 'tran' : 'read' }
    if (!window.rOver) window.rOver = {}
    if (window.rOver.hasOwnProperty(gn())) {
        window.rOver[gn()].style.visibility = window.rOver[gn()].style.visibility === 'visible' ? 'hidden' : 'visible'
    } else {
        window.rOver[gn()] = document.createElement('div')
        var rCan = document.createElement('span')
        var rDrag = document.createElement('span')
        var rPlay = document.createElement('span')
        var rFor = document.createElement('span')
        var rBac = document.createElement('span')
        var rTex = document.createElement('span')
        window.rOver[gn()].style.cssText = window.rOver[gn()].style.cssText + defStyles.popWin + 'z-index: 5;' + (tran ? 'width: 90% !important;' : '')
        window.rOver[gn()].style.visibility = 'visible'
        rCan.innerHTML = defStyles.popCan
        rDrag.innerHTML = defStyles.popDrag
        rPlay.innerHTML = defStyles.popPlay
        rBac.innerHTML = "<strong class='fa fa-fast-backward fa-1x' style='cursor: pointer;'></strong>"
        rFor.innerHTML = "<strong class='fa fa-fast-forward fa-1x' style='cursor: pointer;'></strong>"
        rTex.innerHTML = defStyles.popText
        if (tran) {
            defActions.toTran(
                document.getElementsByClassName(tagName.slice(1))[0], 
                'tranLang', function (j) {
                    rTex.innerHTML = '<br><br>' + j.translation
                }
            )
        }
        window.rOver[gn()].appendChild(rCan)
        window.rOver[gn()].appendChild(rDrag)
        window.rOver[gn()].appendChild(rBac)
        window.rOver[gn()].appendChild(rPlay)
        window.rOver[gn()].appendChild(rFor)
        if (tran) window.rOver[gn()].appendChild(rTex)
        defActions.toDrag(rDrag, window.rOver[gn()])
        defActions.toCan(rCan, window.rOver[gn()])
        defActions.toClicked(rFor)
        defActions.toClicked(rBac)
        var toEndAll = function () { rPlay.innerHTML = defStyles.popPlay }
        rPlay.onclick = function () {
            if (defControl.isPlaying(window[tran ? 'beenTranAll' : 'beenPlayAll'])) defControl.stop(window[tran ? 'beenTranAll' : 'beenPlayAll'])
            else {
                rPlay.innerHTML = defStyles.popPause
                tran && rTex.innerHTML !== defStyles.popText ? defActions.toRead(rTex, 'tranLang', function (j) {
                    defControl.playIt('beenTranAll', j.mp3, toEndAll)
                }) : defActions.toRead(
                    { // work around to remove popup text from main div
                        innerText: document.getElementsByClassName(
                            tagName.slice(1))[0].innerText.replace(
                                defControl.currently_diplayed, '')}
                    , 'readLang', function (j) {
                        defControl.playIt('beenPlayAll', j.mp3, toEndAll)
                })
            }
        }
        rFor.onclick = function () { defControl.fastF(window[tran ? 'beenTranAll' : 'beenPlayAll']) }
        rBac.onclick = function () { defControl.fastB(window[tran ? 'beenTranAll' : 'beenPlayAll']) }
        $(tagName).append(window.rOver[gn()])
    }
}

var showError = function (tagName='.splitIt') {
    // To display popup error message when fetch fails
    window.showedErr = document.createElement('div')
    var eCan = document.createElement('span')
    var eDrag = document.createElement('span')
    var eIco = document.createElement('span')
    var eText = document.createElement('span')
    window.showedErr.style.cssText = window.showedErr.style.cssText + defStyles.popWin + 'z-index: 7;'
    window.showedErr.style.visibility = 'visible'
    eIco.innerHTML = '<strong class="fa fa-2x fa-exclamation-triangle text-danger"></strong>'
    eCan.innerHTML = defStyles.popCan
    eDrag.innerHTML = defStyles.popDrag
    eText.innerHTML = "<br><br>The server is overloaded, try again later."
    defActions.toDrag(eDrag, window.showedErr)
    defActions.toCan(eCan, window.showedErr)
    window.showedErr.appendChild(eCan)
    window.showedErr.appendChild(eDrag)
    window.showedErr.appendChild(eIco)
    window.showedErr.appendChild(eText)
    $(tagName).append(window.showedErr)
}

var theRunner = function (tagName) {
    [].slice.call(document.getElementsByClassName(tagName.slice(1)))
    .forEach(function (e) {
        textTagger(
            e,
            document.getElementById('divider').value.split(';'),
            document.getElementById('actEvent').value.split(','),
            function (curEle) {
                // todo function, takes element if not playing plays it
                defActions.toRead(curEle, 'readLang', function (j) {
                    if (window.beenPlayed) {
                        if (window.beenPlayed.src === window.location.origin + j.mp3) {
                            if (!defControl.isPlaying(window.beenPlayed)) defControl.playIt('beenPlayed', j.mp3)
                        } else {
                            defControl.stop(window.beenPlayed)
                            defControl.playIt('beenPlayed', j.mp3)
                        }
                    } else defControl.playIt('beenPlayed', j.mp3)
                })
            }
        )
    })
}

var tagReady = function (tagName='.splitIt') {
    defControl.stopAll(true)
    defControl.clearAll()
    try { document.divider = document.divider.split(';') }
    catch (e) { document.divider = ['.'] }
    document.readyState === 'complete' ? theRunner(tagName) : window.addEventListener('load', theRunner(tagName))
}



// Extra UI button handlers

var todoOnce = undefined
var storedEditForm = undefined
var storedTitle = undefined
var textForm = function (toEffect) {
    if (!todoOnce) {
        storedEditForm = $('.splitIt').html()
        storedTitle = $('.titleEdit').text()
    }
    if (todoOnce && (storedEditForm !== $('.nicEdit-main').html() || storedTitle !== $('.toAddText').val())) {
        $('#texting').html($('.nicEdit-main').html())
        $('.toEdit').submit()
    } else {
        $('.toEditHide').toggleClass('hidden')
        $('.toRemove').toggleClass('hidden')
        $(toEffect).toggleClass('beatit')
        $('.toEditHide').hasClass('hidden') ? $(toEffect).attr('title', 'Edit your text') : $(toEffect).attr('title', 'Submit updated text')
        if (!todoOnce) {
            // nicEditors({iconsPath: 'https://cdnjs.cloudflare.com/ajax/libs/NicEdit/0.93/nicEditorIcons.gif'}).panelInstance('')
            new nicEditor({iconsPath: 'https://cdnjs.cloudflare.com/ajax/libs/NicEdit/0.93/nicEditorIcons.gif'}).panelInstance('texting')
            $('.nicEdit-main').html($('.splitIt').html())
            $('.toAddText').val($('.titleEdit').text())
            todoOnce = 'defined'
            tagReady()
        }
    }
}

// to resolve previous link
var get_org = function () {
    return window.location.origin + '/' === window.location.href ? 'root' : window.location.href.replace(window.location.origin, '').slice(1)
}