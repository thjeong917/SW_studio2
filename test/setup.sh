#!/usr/bin/expect

spawn fab main

expect ">>"
send "14\r"
expect "all)"
send "127.0.0.1\r"
expect "SUCCESS"
expect ">>"
send "4\r"
expect "name :"
send "test_cluster\r"
expect "count :"
send "1\r"
expect "number :"
send "1\r"
expect "...])"
send {[["nbasearc1 127.0.0.1"]]}
send "\r"
expect ")"
send {["nbasearc1 127.0.0.1"]}
send "\r"
expect "number"
send "1\r"
expect "n]"
send "\r"
expect "n]"
send "\r"
expect "n]"
send "\r"
expect "n]"
send "n\r"
expect "Install"
expect "Uninstall"
expect "======================================="
expect ">>"
send "x\r"
expect eof
