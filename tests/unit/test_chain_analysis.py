""" Crypto Anomaly Detection Engine System (CADES)

Chain Analysis Test Suite

This module implements comprehensive testing for blockchain data analysis components,
including transaction patterns, liquidity tracking, and wallet profiling.

Author: CADES
Team License: Proprietary """

import unittest
from unittest.mock import Mock, patch
import pytest
from src.chain_analysis.blockchain_listener import BlockchainListener
from src.chain_analysis.transaction_analyzer import TransactionAnalyzer
from src.chain_analysis.liquidity_tracker import LiquidityTracker


class TestBlockchainListener(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.listener = BlockchainListener(rpc_endpoint="mock_url")
        self.listener.client = self.mock_client

    @patch('solana.rpc.api.Client.get_block')
    def test_process_new_block(self, mock_get_block):
        mock_block = {
            'blockHeight': 12345,
            'transactions': [
                {
                    'transaction': {
                        'signatures': ['5KtPn1...'],
                        'message': {
                            'accountKeys': ['Address1', 'Address2'],
                            'instructions': [{'programId': 'Program1'}]
                        }
                    }
                }
            ],
            'blockTime': 1678901234
        }
        mock_get_block.return_value = mock_block
        
        result = self.listener.process_new_block(12345)
        self.assertEqual(len(result['transactions']), 1)
        self.assertEqual(result['block_height'], 12345)

    def test_filter_mempool_transactions(self):
        mock_txs = [
            {
                'signature': '5KtPn1...',
                'meta': {
                    'fee': 5000,
                    'preBalances': [1000000, 2000000],
                    'postBalances': [990000, 2010000]
                }
            },
            {
                'signature': '6LuQm2...',
                'meta': {
                    'fee': 5000,
                    'preBalances': [500000, 1000000],
                    'postBalances': [495000, 1005000]
                }
            }
        ]
        filtered = self.listener.filter_mempool_transactions(mock_txs)
        self.assertTrue(len(filtered) > 0)


class TestTransactionAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TransactionAnalyzer()
        with open('tests/fixtures/mock_blockchain_data.json', 'r') as f:
            self.mock_data = json.load(f)
        self.sample_tx = self.mock_data['test_transactions'][0]

    def test_detect_wash_trading(self):
        transactions = [self.sample_tx] * 5
        result = self.analyzer.analyze_transaction(self.sample_tx)
        self.assertIsInstance(result, dict)
        self.assertIn('risk_score', result)

    def test_analyze_cyclic_transactions(self):
        tx_with_cycle = {
            'meta': {
                'innerInstructions': [
                    {
                        'instructions': [
                            {'accounts': ['A', 'B']},
                            {'accounts': ['B', 'C']},
                            {'accounts': ['C', 'A']}
                        ]
                    }
                ]
            }
        }
        result = self.analyzer.analyze_transaction(tx_with_cycle)
        self.assertTrue('cyclic' in result['detected_patterns'])


class TestLiquidityTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = LiquidityTracker()
        
    def test_calculate_liquidity_impact(self):
        pool_data = {
            'token_a_reserve': 1000000,
            'token_b_reserve': 1000000,
            'pool_token_supply': 2000000,
            'mint': 'PoolTokenMint123'
        }
        impact = self.tracker.calculate_liquidity_impact(100000, pool_data)
        self.assertIsInstance(impact, float)
        self.assertTrue(0 <= impact <= 1)

    def test_detect_liquidity_removal(self):
        events = [
            {
                'signature': '5KtPn1...',
                'meta': {
                    'preTokenBalances': [{'uiAmount': 1000}],
                    'postTokenBalances': [{'uiAmount': 0}]
                }
            },
            {
                'signature': '6LuQm2...',
                'meta': {
                    'preTokenBalances': [{'uiAmount': 2000}],
                    'postTokenBalances': [{'uiAmount': 0}]
                }
            }
        ]
        threshold = 0.1
        is_suspicious = self.tracker.detect_liquidity_removal(events, threshold)
        self.assertIsInstance(is_suspicious, bool)

if __name__ == '__main__':
    unittest.main()