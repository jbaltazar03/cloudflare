#!/usr/bin/env python3
import cloudflare

cf = cloudflare.Get()

# cf._verify_token()

# cf.users()
# cf.organizations()
# cf.zones()
# cf.ssl_count()
# cf.rate_limit()


######## This is for cops inventory #######
# cf.custom_ssl_count()
cf.custom_rate_limit()
cf.dns_zones()

