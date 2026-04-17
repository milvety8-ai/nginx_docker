#!/bin/bash
PASS=0; FAIL=0
check() { local desc=$1; local cmd=$2; local expected=$3
  result=$(eval $cmd 2>/dev/null)
  if echo "$result" | grep -q "$expected"; then
    echo "✅ $desc"; PASS=$((PASS+1))
  else
    echo "❌ $desc (got: $result)"; FAIL=$((FAIL+1))
  fi
}

check "Static HTML serves"         "curl -ks -o /dev/null -w '%{http_code}' https://localhost/" "200"
check "NGINX hides version"        "curl -ksI https://localhost/ | tr -d '\r' | grep -i '^server: nginx$'" "nginx"
check "Gzip enabled"               "curl -ksI -H 'Accept-Encoding: gzip' https://localhost/ | tr -d '\r' | grep -i '^content-encoding:'" "gzip"
check "404 custom page"            "curl -ks -o /dev/null -w '%{http_code}' https://localhost/x" "404"
check "API v1 proxy works"         "curl -s http://api.localhost/api/v1/info"              "v1"
check "API v2 proxy works"         "curl -s http://api.localhost/api/v2/info"              "v2"
check "HTTPS redirect"             "curl -sI http://localhost/ | grep -i location"         "https"
check "HTTPS works"                "curl -ks https://localhost/ | grep -i html"            "html"
check "Rate limit returns 429"     "for i in {1..40}; do curl -s -o /dev/null -w '%{http_code}\n' http://secure.localhost/api/v1/info; done | grep 429" "429"
check "Cache HIT on 2nd request"   "curl -s http://api.localhost/api/cached/info > /dev/null && curl -sI http://api.localhost/api/cached/info | grep X-Cache" "HIT"

echo ""; echo "Results: $PASS passed, $FAIL failed"
