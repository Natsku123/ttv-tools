import axios, {Axios} from 'axios';
import { wrapper } from 'axios-cookiejar-support';
import { CookieJar } from 'tough-cookie';

const WebStorageCookieStore =  require('tough-cookie-web-storage-store');
const qs = require('qs');


let client: Axios;

if (typeof window === 'undefined') {
    client = wrapper(axios.create({ withCredentials: true, paramsSerializer: params => qs.stringify(params, {arrayFormat: 'repeat'})}));
} else {
    let store = new WebStorageCookieStore(localStorage);
    const jar = new CookieJar(store, {rejectPublicSuffixes: false});
    client = axios.create({ jar, withCredentials: true, paramsSerializer: params => qs.stringify(params, {arrayFormat: 'repeat'}) });
}


export {
    client
}