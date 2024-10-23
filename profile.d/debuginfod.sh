# $HOME/.profile* or similar files may first set $DEBUGINFOD_URLS.
# If $DEBUGINFOD_URLS is not set there, we set it from system *.url files.
# $HOME/.*rc or similar files may then amend $DEBUGINFOD_URLS.
# See also [man debuginfod-client-config] for other environment variables
# such as $DEBUGINFOD_MAXSIZE, $DEBUGINFOD_MAXTIME, $DEBUGINFOD_PROGRESS.

prefix="/usr"
if [ -z "$DEBUGINFOD_URLS" ]; then
    DEBUGINFOD_URLS=$(cat /dev/null "/etc/debuginfod"/*.urls 2>/dev/null | tr '\n' ' ' || :)
    [ -n "$DEBUGINFOD_URLS" ] && export DEBUGINFOD_URLS || unset DEBUGINFOD_URLS
fi

if [ -z "$DEBUGINFOD_IMA_CERT_PATH" ]; then
    DEBUGINFOD_IMA_CERT_PATH=$(cat /dev/null "/etc/debuginfod"/*.certpath 2>/dev/null | tr '\n' ':' || :)
    [ -n "$DEBUGINFOD_IMA_CERT_PATH" ] && export DEBUGINFOD_IMA_CERT_PATH || unset DEBUGINFOD_IMA_CERT_PATH
fi
unset prefix
