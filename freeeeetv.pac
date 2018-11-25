//http://proxy.freeeeetv.com:8000/test.pac
function FindProxyForURL(url, host) {
  var PROXY = "PROXY proxy.freeeeetv.com:8002";
  var DEFAULT = "DIRECT";
  if(/trailers\.apple\.com/i.test(url)) return PROXY;
  if(/www\.showtime\.com/i.test(url)) return PROXY;
//  if(/player\.aetndigital\.com/i.test(url)) return PROXY;
//  if(/appletv\.crackle\.com/i.test(url)) return PROXY;
//  if(/watchabc\.go\.com/i.test(url)) return PROXY;
  return DEFAULT;
}
