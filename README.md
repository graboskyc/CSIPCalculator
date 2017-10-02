# CSIPCalculator
The CloudShell IP Calculator

## Background
This is a basic first pass at management of IP Addresses. It is ideally meant to dish out point to point links(/30 or /31) from a larger address pool (like a /24) from within Quali CloudShell.

## Use
Import the environment package. This creates a /24 "container" called "HomeNetwork".

Create a sandbox and add the "Address Finder" service to it. You can also add the attribute of "Auto Add to Sandbox" so it always gets added to every sandbox. It is "admin only" so it will be invisible to normal users.

Run the command `printIPsInContainer("HomeNetwork")` for it to dump all 256 IPs in this block. To reserve the next /30 within the current running sandbox, run `getNextIP("HomeNetwork","30")` and it will reserve the first 4 addresses and put them in the sandbox. The command will return the JSON of the full path of these 4 IPs.

There is some basic error handling to confirm the container exists, the requested size is small enough for the container, and the container has that many IPs.

For it to manage things like Management IPs where you want to request a single IP, use 32 as the CIDR input.

## Screenshots
![](/Screenshots/SS01.jpg)
![](/Screenshots/SS02.jpg)

## Notice
This is a preliminary work in progress. It does not currently enforce basic subnetting principals (like given a /24, requesting a /30, then requesting a /25 will not have your offsets correct). Right now it is really meant to give out /30s given a /24 to start with, or management IPs.