'use strict';

const BTV_BASE_URL = 'https://boilertvondemand-housing-purdue-edu.swankmp.net';

class BreadCrumbs {
    labels = [];
    elems = [];

    step(label, elems) {
        this.labels.push(label);
        this.elems.push(elems);

        if (elems == undefined || elems == null || elems.length == 0) {
            console.warn('Got missing element at step: ' + this.line());
            this.trace();
            console.warn('End missing element');
        }
    }

    printLine() {
        console.log(this.line());
    }

    line() {
        return this.labels.join(' -> ');
    }

    trace() {
        for (let i = 0; i < this.labels.length; i++) {
            console.log(this.labels[i]);
            console.log(this.elems[i]);
        }
    }

    last() {
        const lastIndex = this.labels.length - 1
        console.log(this.labels[lastIndex]);
        console.log(this.elems[lastIndex]);
    }
}

/**
 * Process the price, link, and logo for the <a> element
 * that Google uses for each streaming service.
 *
 * @param {HTMLAnchorElement} a
 * @param {string} btvUrl
 * @param {BreadCrumbs|null} breadCrumbs
 */
function google_overwrite_service_entry_a(a, btvUrl, breadCrumbs) {

    breadCrumbs = breadCrumbs || new BreadCrumbs();

    if (a.nodeName != 'A') {
        console.error('Expected element to be an "A" node. Got: ' + a.nodeName);
    }

    // Replace the logo with Purdue logo
    let logos = a.getElementsByTagName('img');
    breadCrumbs.step('<img>', logos);

    let logo = logos[0];
    breadCrumbs.step('[0]', logo);

    // Replace the price with Free
    let spans = a.getElementsByTagName('span');
    breadCrumbs.step('<span>', spans);

    let price = null;
    for (let span of spans) {
        if (span.innerHTML.includes('$') || span.innerHTML.includes('Free')) {
            price = span;
            break;
        }
    }
    breadCrumbs.step('span.includes($)', price);

    a.href = btvUrl;
    logo.src = chrome.extension.getURL('/icons/purdue-logo-square.svg');
    price.parentElement.innerHTML = 'Free';     // Go up one element to also clear the "From "

    // This is pretty wacky, but we need to set the name for "All watch options" entries
    if (logo.parentElement.parentElement.children[1] && logo.parentElement.parentElement.children[1].children[0]) {
        logo.parentElement.parentElement.children[1].children[0].innerHTML = 'Purdue BTV';
    }

    return a;
}

if (location.hostname.endsWith('google.com')) {
    console.log('Matched Google');

    // Get the movie name
    let tBreadCrumbs = new BreadCrumbs();

    let titleElems = document.querySelectorAll('h2[data-attrid="title"]');
    tBreadCrumbs.step('<h2 data-attrid="title">', titleElems);

    let titleElem = titleElems[0];
    tBreadCrumbs.step('[0]', titleElem);

    let titleSpan = titleElem.getElementsByTagName('span')[0];
    tBreadCrumbs.step('<span>[0]', titleSpan);

    let title = titleSpan.innerText;
    tBreadCrumbs.step('.innerText', title);

    tBreadCrumbs.printLine();
    tBreadCrumbs.trace();

    // TODO: Search API

    // Switch the watch information
    let wBreadCrumbs = new BreadCrumbs();

    // kc:/film/film:media_actions_wholepage
    let mediaActions = document.querySelectorAll('div[data-attrid*="film/film:media_action"]');
    wBreadCrumbs.step('<div data-attrid="film/film:media_action">', mediaActions);

    let mediaAction = mediaActions[0];
    wBreadCrumbs.step('[0]', mediaAction);

    let watchNows = mediaAction.getElementsByTagName('a');
    wBreadCrumbs.step('<a>', watchNows);

    let watchNow = watchNows[0];
    wBreadCrumbs.step('[0]', watchNow);

    // See if the movie is already free
    // BTV isn't our first pick if one of the other services is free
    if (!watchNow.innerHTML.includes('Free')) {
        console.log('Movie is non-free. Overwriting exterior watch option');
        console.log('Has dollar sign: ' + watchNow.innerHTML.includes('$'));

        // TODO: Put in real URL from API response
        watchNow = google_overwrite_service_entry_a(watchNow, BTV_BASE_URL, wBreadCrumbs);
    }

    // Insert into the "All watch options"
    let aBreadCrumbs = new BreadCrumbs();

    let watchFilms = document.querySelectorAll('div[data-attrid*="action:watch_film"]');
    aBreadCrumbs.step('<div data-attrid="action:watch_film">', watchFilms);

    let watchFilm = watchFilms[0];
    aBreadCrumbs.step('[0]', watchFilm);

    let container = watchFilm.getElementsByTagName('g-expandable-container')[0];
    aBreadCrumbs.step('<g-expandable-container>[0]', container);

    // Our direct parent is not the container
    let containerEntries = container.getElementsByTagName('g-expandable-content');
    aBreadCrumbs.step('<g-expandable-content>', containerEntries);

    let newEntry = containerEntries[0].cloneNode(true);
    newEntry.style.maxHeight = '61px';  // Turn this on or it'll never show
    aBreadCrumbs.step('clone', newEntry);

    let newEntryA = newEntry.getElementsByTagName('a')[0];
    aBreadCrumbs.step('<a>]0]', newEntryA);

    newEntryA = google_overwrite_service_entry_a(newEntryA, BTV_BASE_URL, aBreadCrumbs);
    aBreadCrumbs.step('overwrite', newEntryA);

    // Find the first non-free service so that we can insert before it
    let beforeEntry = containerEntries[0];
    for (let entry of containerEntries) {
        console.log(entry);
        if (!entry.innerHTML.includes('Free')) {
            beforeEntry = entry;
            break;
        }
    }
    containerEntries[0].parentElement.insertBefore(newEntry, beforeEntry);
    console.log(newEntry);
}