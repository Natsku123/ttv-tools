import axios from 'axios';
import { wrapper } from 'axios-cookiejar-support';
import { CookieJar } from 'tough-cookie';

import WebStorageCookieStore from 'tough-cookie-web-storage-store';

let client;

if (typeof window === 'undefined') {
    client = wrapper(axios.create({ withCredentials: true}));
} else {
    let store = new WebStorageCookieStore(localStorage);
    const jar = new CookieJar(store, {rejectPublicSuffixes: false});
    client = axios.create({ jar, withCredentials: true });
}


export {
    client
}