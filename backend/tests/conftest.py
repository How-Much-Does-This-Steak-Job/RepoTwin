"""Pytest configuration and fixtures for RepoTwin backend tests."""

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

# Add the backend app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.models.database import Base, Repository, Analysis, RepositoryStatus, AnalysisStatus


# ============== Configuration ==============

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============== Database Fixtures ==============

@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Get test database URL."""
    return os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://test:test@localhost/repotwin_test")


@pytest.fixture(scope="session")
def sync_test_database_url() -> str:
    """Get synchronous test database URL for setup."""
    return os.getenv("SYNC_TEST_DATABASE_URL", "postgresql://test:test@localhost/repotwin_test")


@pytest.fixture(scope="session")
def setup_test_db(sync_test_database_url: str):
    """Set up test database tables."""
    engine = create_engine(sync_test_database_url)
    
    # Drop all tables and recreate
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest_asyncio.fixture
async def db_session(setup_test_db, test_database_url) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    engine = create_async_engine(test_database_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        yield session
        # Rollback any changes after test
        await session.rollback()
    
    await engine.dispose()


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = MagicMock()
    session.get = AsyncMock()
    return session


# ============== Redis Fixtures ==============

@pytest.fixture
def mock_redis():
    """Create a mock Redis client."""
    redis = MagicMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock(return_value=True)
    redis.delete = AsyncMock(return_value=1)
    redis.expire = AsyncMock(return_value=True)
    redis.setex = AsyncMock(return_value=True)
    redis.keys = AsyncMock(return_value=[])
    redis.flushdb = AsyncMock(return_value=True)
    redis.hget = AsyncMock(return_value=None)
    redis.hset = AsyncMock(return_value=1)
    redis.hgetall = AsyncMock(return_value={})
    redis.publish = AsyncMock(return_value=1)
    redis.lpush = AsyncMock(return_value=1)
    redis.rpop = AsyncMock(return_value=None)
    redis.llen = AsyncMock(return_value=0)
    return redis


@pytest.fixture
def mock_redis_pool():
    """Create a mock Redis connection pool."""
    pool = MagicMock()
    pool.get_redis = MagicMock()
    return pool


# ============== Model Fixtures ==============

@pytest.fixture
def sample_repo_id() -> uuid.UUID:
    """Sample repository ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_analysis_id() -> uuid.UUID:
    """Sample analysis ID."""
    return uuid.uuid4()


@pytest.fixture
def sample_repository(sample_repo_id: uuid.UUID) -> Repository:
    """Create a sample repository."""
    return Repository(
        id=sample_repo_id,
        name="test-repo",
        full_name="test-user/test-repo",
        provider="github",
        url="https://github.com/test-user/test-repo",
        clone_url="https://github.com/test-user/test-repo.git",
        default_branch="main",
        description="Test repository",
        private=False,
        language="python",
        languages={"python": 1000, "javascript": 500},
        stats={"files_count": 50, "lines_of_code": 5000},
        status=RepositoryStatus.ACTIVE,
        storage_path="/tmp/repos/test-repo",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_analysis(sample_analysis_id: uuid.UUID, sample_repo_id: uuid.UUID) -> Analysis:
    """Create a sample analysis."""
    return Analysis(
        id=sample_analysis_id,
        repository_id=sample_repo_id,
        description="Refactor PaymentProcessor to use new PaymentGateway API",
        change_type="refactor",
        context={
            "files": [{"path": "src/payment.py", "line_start": 1, "line_end": 100}],
            "functions": [{"file_path": "src/payment.py", "name": "process_payment"}],
        },
        options={"include_tests": True, "include_implementation_plan": True},
        status=AnalysisStatus.COMPLETED,
        progress=100,
        created_at=datetime.now(timezone.utc),
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        duration_seconds=45.5,
        results={
            "summary": {
                "title": "Payment Gateway Refactor Analysis",
                "overview": "This change affects the payment processing system",
                "key_points": ["8 files affected", "Medium risk level"],
            },
            "affected_files": [
                {
                    "path": "src/payment.py",
                    "impact_level": "direct",
                    "change_type": "modification",
                    "reasoning": "Core payment logic",
                }
            ],
            "impact_radius": {
                "category": "medium",
                "metrics": {
                    "files_affected": 8,
                    "files_direct": 3,
                    "files_indirect": 5,
                },
            },
            "risk_assessment": {
                "overall_level": "medium",
                "score": 65,
                "factors": [],
            },
        },
        risk_level="medium",
        impact_radius_category="medium",
        files_affected_count=8,
        functions_affected_count=15,
    )


# ============== Mock External Services ==============

@pytest.fixture
def mock_watsonx_response() -> str:
    """Sample IBM watsonx.ai response."""
    return """{
        "summary": {
            "title": "Impact Analysis Results",
            "overview": "This change affects approximately 8 files with medium risk level.",
            "key_points": [
                "8 files require modifications",
                "Primary impact on core business logic",
                "Test coverage should be increased"
            ]
        },
        "affected_files": [
            {
                "path": "src/main.py",
                "impact_level": "direct",
                "change_type": "modification",
                "reasoning": "Primary file containing core logic",
                "lines_added": 25,
                "lines_removed": 10,
                "complexity_change": "neutral",
                "risk_factors": ["Core business logic"]
            }
        ],
        "impact_radius": {
            "category": "medium",
            "metrics": {
                "files_affected": 8,
                "files_direct": 3,
                "files_indirect": 5,
                "functions_affected": 15,
                "classes_affected": 4,
                "tests_affected": 6,
                "percentage_of_codebase": 5.2
            }
        },
        "risk_assessment": {
            "overall_level": "medium",
            "score": 65,
            "factors": [
                {
                    "name": "API Compatibility",
                    "level": "medium",
                    "likelihood": "medium",
                    "impact": "high",
                    "description": "Changes may affect public API signatures",
                    "mitigation": "Add deprecation warnings"
                }
            ]
        },
        "regression_analysis": {
            "breaking_changes": [],
            "behavior_changes": [
                {
                    "type": "error_handling",
                    "file": "src/main.py",
                    "description": "Error handling behavior may change",
                    "impact": "Existing error handling may need updates"
                }
            ]
        },
        "implementation_plan": {
            "phases": [
                {
                    "phase": 1,
                    "name": "Update Core Logic",
                    "description": "Implement the primary changes",
                    "files": ["src/main.py"],
                    "estimated_effort": "2 hours",
                    "checkpoints": ["Unit tests pass"]
                }
            ],
            "total_estimated_effort": "4 hours",
            "rollback_strategy": "Revert to previous commit",
            "prerequisites": ["Database backup"]
        },
        "test_recommendations": {
            "existing_tests_to_update": [
                {
                    "path": "tests/test_main.py",
                    "changes": "Update test cases for new behavior",
                    "priority": "high"
                }
            ],
            "new_tests_needed": [
                {
                    "type": "unit",
                    "description": "Test new edge cases",
                    "priority": "medium"
                }
            ],
            "coverage_gaps": []
        }
    }"""


@pytest.fixture
def mock_github_response():
    """Sample GitHub API response for repository."""
    return {
        "id": 123456,
        "name": "test-repo",
        "full_name": "test-user/test-repo",
        "private": False,
        "html_url": "https://github.com/test-user/test-repo",
        "clone_url": "https://github.com/test-user/test-repo.git",
        "default_branch": "main",
        "language": "Python",
        "description": "Test repository",
        "stargazers_count": 10,
        "forks_count": 5,
    }


# ============== Test Data Fixtures ==============

@pytest.fixture
def sample_python_code() -> str:
    """Sample Python code for parsing tests."""
    return '''
"""Payment processing module."""
import logging
from typing import Optional
from datetime import datetime

from .gateway import PaymentGateway
from .models import Payment, Transaction

logger = logging.getLogger(__name__)


class PaymentProcessor:
    """Process payments through various gateways."""
    
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.logger = logger
    
    def process_payment(
        self, 
        amount: float, 
        currency: str = "USD",
        customer_id: Optional[str] = None
    ) -> Transaction:
        """Process a payment transaction."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if currency not in ["USD", "EUR", "GBP"]:
            raise ValueError(f"Unsupported currency: {currency}")
        
        payment = Payment(
            amount=amount,
            currency=currency,
            customer_id=customer_id,
            created_at=datetime.now()
        )
        
        result = self.gateway.charge(payment)
        
        if result.success:
            self.logger.info(f"Payment processed: {result.transaction_id}")
        else:
            self.logger.error(f"Payment failed: {result.error}")
        
        return result
    
    def refund_payment(self, transaction_id: str) -> Transaction:
        """Refund a previous transaction."""
        return self.gateway.refund(transaction_id)


class StripeGateway(PaymentGateway):
    """Stripe payment gateway implementation."""
    
    def charge(self, payment: Payment) -> Transaction:
        # Stripe-specific implementation
        pass
    
    def refund(self, transaction_id: str) -> Transaction:
        # Stripe-specific implementation
        pass
'''


@pytest.fixture
def sample_javascript_code() -> str:
    """Sample JavaScript code for parsing tests."""
    return '''
import React, { useState, useEffect } from 'react';
import { PaymentService } from './services/PaymentService';
import { formatCurrency } from './utils/currency';

/**
 * Payment form component
 * @param {Object} props
 * @param {Function} props.onSubmit
 * @param {number} props.defaultAmount
 */
export function PaymentForm({ onSubmit, defaultAmount = 0 }) {
    const [amount, setAmount] = useState(defaultAmount);
    const [currency, setCurrency] = useState('USD');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (amount < 0) {
            setError('Amount must be positive');
        } else {
            setError(null);
        }
    }, [amount]);

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        
        try {
            const result = await PaymentService.process({
                amount,
                currency,
            });
            onSubmit(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
            />
            <select value={currency} onChange={(e) => setCurrency(e.target.value)}>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
            </select>
            <button type="submit" disabled={loading}>
                {loading ? 'Processing...' : 'Pay'}
            </button>
        </form>
    );
}

export default PaymentForm;
'''


@pytest.fixture
def sample_typescript_code() -> str:
    """Sample TypeScript code for parsing tests."""
    return '''
import { Injectable } from '@nestjs/common';
import { Repository } from 'typeorm';
import { InjectRepository } from '@nestjs/typeorm';

import { Payment } from './entities/payment.entity';
import { PaymentGateway } from './interfaces/payment-gateway.interface';

interface ProcessPaymentDto {
    amount: number;
    currency: string;
    customerId?: string;
}

@Injectable()
export class PaymentService {
    constructor(
        @InjectRepository(Payment)
        private readonly paymentRepository: Repository<Payment>,
        private readonly gateway: PaymentGateway,
    ) {}

    async processPayment(dto: ProcessPaymentDto): Promise<Payment> {
        const { amount, currency, customerId } = dto;

        if (amount <= 0) {
            throw new Error('Amount must be positive');
        }

        const payment = this.paymentRepository.create({
            amount,
            currency,
            customerId,
            status: 'pending',
        });

        const result = await this.gateway.charge(payment);
        
        payment.status = result.success ? 'completed' : 'failed';
        payment.transactionId = result.transactionId;

        return this.paymentRepository.save(payment);
    }

    async refundPayment(paymentId: string): Promise<Payment> {
        const payment = await this.paymentRepository.findOne({
            where: { id: paymentId },
        });

        if (!payment) {
            throw new Error('Payment not found');
        }

        await this.gateway.refund(payment.transactionId);
        payment.status = 'refunded';

        return this.paymentRepository.save(payment);
    }
}
'''


@pytest.fixture
def sample_java_code() -> str:
    """Sample Java code for parsing tests."""
    return '''
package com.example.payment;

import java.util.Optional;
import java.math.BigDecimal;
import java.time.LocalDateTime;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Autowired;

import com.example.payment.model.Payment;
import com.example.payment.model.Transaction;
import com.example.payment.gateway.PaymentGateway;

/**
 * Service for processing payments
 */
@Service
public class PaymentService {
    
    private final PaymentGateway gateway;
    private final PaymentRepository repository;
    
    @Autowired
    public PaymentService(PaymentGateway gateway, PaymentRepository repository) {
        this.gateway = gateway;
        this.repository = repository;
    }
    
    public Transaction processPayment(BigDecimal amount, String currency, String customerId) {
        if (amount.compareTo(BigDecimal.ZERO) <= 0) {
            throw new IllegalArgumentException("Amount must be positive");
        }
        
        Payment payment = new Payment();
        payment.setAmount(amount);
        payment.setCurrency(currency);
        payment.setCustomerId(customerId);
        payment.setCreatedAt(LocalDateTime.now());
        
        return gateway.charge(payment);
    }
    
    public Optional<Transaction> refundPayment(String transactionId) {
        return gateway.refund(transactionId);
    }
}
'''


@pytest.fixture
def sample_go_code() -> str:
    """Sample Go code for parsing tests."""
    return '''
package payment

import (
    "context"
    "errors"
    "time"
    
    "github.com/example/payment/gateway"
    "github.com/example/payment/models"
)

// PaymentProcessor handles payment transactions
type PaymentProcessor struct {
    gateway gateway.PaymentGateway
    repo    Repository
}

// NewPaymentProcessor creates a new payment processor
func NewPaymentProcessor(g gateway.PaymentGateway, r Repository) *PaymentProcessor {
    return &PaymentProcessor{
        gateway: g,
        repo:    r,
    }
}

// ProcessPayment processes a payment transaction
func (p *PaymentProcessor) ProcessPayment(ctx context.Context, amount float64, currency string) (*models.Transaction, error) {
    if amount <= 0 {
        return nil, errors.New("amount must be positive")
    }
    
    payment := &models.Payment{
        Amount:    amount,
        Currency:  currency,
        CreatedAt: time.Now(),
    }
    
    result, err := p.gateway.Charge(ctx, payment)
    if err != nil {
        return nil, err
    }
    
    if err := p.repo.Save(result); err != nil {
        return nil, err
    }
    
    return result, nil
}
'''


# ============== Utility Fixtures ==============

@pytest.fixture
def temp_repo_dir(tmp_path):
    """Create a temporary repository directory structure."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()
    
    # Create some source files
    src_dir = repo_dir / "src"
    src_dir.mkdir()
    
    (src_dir / "main.py").write_text("def main(): pass")
    (src_dir / "utils.py").write_text("def helper(): pass")
    
    tests_dir = repo_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_main.py").write_text("def test_main(): pass")
    
    return repo_dir


@pytest.fixture
def mock_settings():
    """Mock application settings."""
    with patch("app.config.settings") as settings:
        settings.watsonx_api_key = "test-api-key"
        settings.watsonx_project_id = "test-project-id"
        settings.watsonx_url = "https://test.watsonx.ai"
        settings.watsonx_model_id = "ibm/granite-13b-chat-v2"
        settings.watsonx_max_tokens = 4000
        settings.watsonx_temperature = 0.1
        settings.watsonx_top_p = 0.9
        settings.database_url = "postgresql://test:test@localhost/test"
        settings.redis_url = "redis://localhost:6379/0"
        settings.secret_key = "test-secret-key"
        yield settings


# ============== Async Helpers ==============

@pytest.fixture
def async_return():
    """Helper to create async return values."""
    def _async_return(value):
        async def _inner(*args, **kwargs):
            return value
        return _inner
    return _async_return


@pytest.fixture
def raise_exception():
    """Helper to raise exceptions in async mocks."""
    def _raise_exception(exc):
        async def _inner(*args, **kwargs):
            raise exc
        return _inner
    return _raise_exception
