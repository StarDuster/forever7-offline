from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
try:
    from dnslib import DNSRecord, QTYPE
    from local_patch_dns import dns_answer
except ImportError:
    DNSRecord = None


@unittest.skipIf(DNSRecord is None, 'Run with toolchains/proxy-venv/bin/python')
class DirectPatchDNSTests(unittest.TestCase):
    def test_only_exact_patch_hosts_resolve_to_local_ipv4(self):
        for host in ('g58.update.netease.com', 'G58.GPH.NETEASE.COM.'):
            query = DNSRecord.question(host)
            def forbidden(_):
                self.fail('Patch hostname must not escape to upstream DNS')
            reply = DNSRecord.parse(dns_answer(query.pack(), '10.65.9.251', forbidden))
            self.assertEqual(reply.header.id, query.header.id)
            self.assertEqual(str(reply.rr[0].rdata), '10.65.9.251')
            self.assertEqual(reply.rr[0].ttl, 5)

    def test_unrelated_and_suffix_lookalike_names_are_forwarded_unchanged(self):
        for host in ('example.com', 'not-g58.update.netease.com',
                     'g58.update.netease.com.example.com'):
            query = DNSRecord.question(host)
            packet = query.pack()
            seen = []
            expected = query.reply().pack()
            actual = dns_answer(packet, '10.65.9.251', lambda value: (seen.append(value) or expected))
            self.assertEqual(actual, expected)
            self.assertEqual(seen, [packet])

    def test_patch_ipv6_and_https_service_records_do_not_reveal_public_endpoints(self):
        for query_type in ('AAAA', 'HTTPS'):
            query = DNSRecord.question('g58.gph.netease.com', query_type)
            reply = DNSRecord.parse(dns_answer(query.pack(), '10.65.9.251', lambda _: self.fail()))
            self.assertEqual(reply.header.rcode, 0)
            self.assertFalse(reply.rr)

    def test_multi_question_packets_are_rejected(self):
        query = DNSRecord.question('g58.update.netease.com')
        query.add_question(DNSRecord.question('example.com').q)
        with self.assertRaises(ValueError):
            dns_answer(query.pack(), '10.65.9.251', lambda _: self.fail())


if __name__ == '__main__':
    unittest.main()
