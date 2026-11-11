### What Happened?

Starting on 21 October, customers were unable to transmit ICS2 customs submissions through CargoWise due to authorisation rejections. Our investigation identified two overlapping failures: a temporary authorisation issue in the external ICS2 system and an expired WiseTech transport certificate that prevented message transmission.

### How did we respond?

Our Major Incident Management process was initiated to coordinate the response. Our engineers identified both the external authorisation failures and the expired transport certificate, then restored service by reconfiguring an existing signing certificate as the transport certificate. Our support team then guided customers to resubmit rejected filings.

### Additional steps we're taking

We are pursuing replacement transport certificates through multiple vendors (PSW/D-Trust and DigiCert) to implement a permanent fix and prevent expiry-related failures in the future. The procurement of these permanent replacement certificates will ensure ongoing compliance with mTLS requirements and eliminate the dependency on temporary workarounds. 

We are continually improving our processes and infrastructure and take any service interruption seriously. Please be assured that this event has received highest level of attention from our engineering and management teams.
