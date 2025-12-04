# Testing Methodology & Best Practices

## Overview

This document captures the systematic approach used to design and implement the comprehensive test suite for the PCO API Wrapper project. It serves as a guide for tackling complex testing scenarios with branching logic, dependencies, and edge cases.

---

## The Challenge

When testing workflows with complex branching logic, several challenges emerge:

1. **Overwhelming Dependencies** - Multiple interconnected components
2. **Edge Cases** - Numerous scenarios that need coverage
3. **Test Duplication** - Risk of redundant test cases
4. **Coverage Gaps** - Missing critical paths
5. **Maintenance Burden** - Difficult to update as code evolves

---

## Our Systematic Approach

### Phase 1: Decomposition & Analysis

#### Step 1: Map the Workflow
Break down complex workflows into discrete, testable units:

```
Complex Workflow: create_or_update_person()
├── Check if person exists (find_person_by_name)
│   ├── Person found → Update path
│   └── Person not found → Create path
├── Update attributes if needed
│   ├── Gender changed → Update
│   ├── Birthdate changed → Update
│   └── No changes → Skip
└── Handle email
    ├── Email provided
    │   ├── Email exists → Skip
    │   └── Email new → Add
    └── No email → Skip
```

#### Step 2: Identify Decision Points
List all branching points and their outcomes:

| Decision Point | Possible Outcomes | Test Required |
|----------------|-------------------|---------------|
| Person exists? | Yes / No | 2 tests |
| Attributes changed? | Yes / No | 2 tests |
| Email provided? | Yes / No | 2 tests |
| Email exists? | Yes / No | 2 tests |

#### Step 3: Calculate Path Coverage
Use decision point analysis to determine minimum test cases:

- **Total Paths**: 2 × 2 × 2 × 2 = 16 possible combinations
- **Critical Paths**: 6-8 tests cover most important scenarios
- **Edge Cases**: 3-4 additional tests for error conditions

---

### Phase 2: Test Design Strategy

#### 1. **Happy Path Tests** (Success Scenarios)
Test the most common, successful workflows first:

```python
def test_create_new_person():
    """Test creating a person when they don't exist"""
    # Covers: Person not found → Create → Success
    
def test_update_existing_person():
    """Test updating an existing person"""
    # Covers: Person found → Update → Success
    
def test_create_with_email():
    """Test creating person with email"""
    # Covers: Create → Add email → Success
```

#### 2. **Alternative Path Tests** (Valid Variations)
Test valid but less common scenarios:

```python
def test_update_no_changes_needed():
    """Test when person exists but no updates needed"""
    # Covers: Person found → No changes → Skip update
    
def test_skip_existing_email():
    """Test that existing email is not added again"""
    # Covers: Email exists → Skip add
```

#### 3. **Error Path Tests** (Failure Scenarios)
Test how the system handles errors:

```python
def test_api_error_during_create():
    """Test handling of API errors"""
    # Covers: Create → API Error → Handle gracefully
    
def test_invalid_data():
    """Test with invalid input data"""
    # Covers: Validation → Reject → Error message
```

#### 4. **Edge Case Tests** (Boundary Conditions)
Test unusual but valid scenarios:

```python
def test_empty_email_list():
    """Test person with no emails"""
    # Covers: Edge case → Empty list handling
    
def test_multiple_emails():
    """Test person with multiple emails"""
    # Covers: Edge case → List iteration
```

---

### Phase 3: Avoiding Duplication

#### Technique 1: Test Fixtures
Extract common setup into reusable fixtures:

```python
@pytest.fixture
def existing_person(mock_pco_client):
    """Fixture for an existing person"""
    person = create_mock_person('123', 'John', 'Doe')
    mock_pco_client.iterate.return_value = [person]
    return person

# Use in multiple tests
def test_update_person(existing_person):
    # Reuse setup
    
def test_delete_person(existing_person):
    # Reuse setup
```

#### Technique 2: Parameterized Tests
Test multiple scenarios with one test function:

```python
@pytest.mark.parametrize("gender,expected", [
    ("Male", "Male"),
    ("Female", "Female"),
    (None, None),
])
def test_gender_values(gender, expected):
    """Test various gender values"""
    # One test, multiple scenarios
```

#### Technique 3: Test Hierarchies
Organize tests by functionality:

```python
class TestPersonCreation:
    """All tests related to creating people"""
    def test_create_minimal()
    def test_create_with_all_fields()
    def test_create_duplicate_check()

class TestPersonUpdate:
    """All tests related to updating people"""
    def test_update_single_field()
    def test_update_multiple_fields()
    def test_update_no_changes()
```

---

### Phase 4: Coverage Verification

#### 1. Code Coverage Analysis
```bash
# Generate coverage report
pytest tests/unit --cov=src --cov-report=html --cov-report=term-missing

# Identify uncovered lines
pytest tests/unit --cov=src --cov-report=term-missing | grep "MISS"
```

#### 2. Decision Coverage Matrix
Track which decision points are tested:

| Function | Decision Point | Covered | Test Name |
|----------|---------------|---------|-----------|
| create_or_update_person | Person exists? | ✅ | test_update_existing_person |
| create_or_update_person | Person not found? | ✅ | test_create_new_person |
| create_or_update_person | Email provided? | ✅ | test_create_with_email |
| create_or_update_person | Email exists? | ✅ | test_skip_existing_email |

#### 3. Integration Testing
Verify end-to-end workflows:

```python
def test_complete_person_lifecycle():
    """Test create → read → update → delete"""
    # Ensures all components work together
```

---

## Practical Example: Testing `create_or_update_person()`

### Step 1: Analyze the Function

```python
def create_or_update_person(pco, first_name, last_name, gender=None, 
                           birthdate=None, email=None, email_location="Work"):
    # Decision 1: Does person exist?
    person = find_person_by_name(pco, first_name, last_name)
    
    if not person:
        # Path A: Create new person
        person = add_person(pco, first_name, last_name, gender, birthdate)
    else:
        # Path B: Update existing person
        # Decision 2: Do attributes need updating?
        updates = {}
        if gender and person['attributes'].get('gender') != gender:
            updates['gender'] = gender
        if birthdate and person['attributes'].get('birthdate') != birthdate:
            updates['birthdate'] = birthdate
        
        if updates:
            update_person_attributes(pco, person['id'], updates)
    
    # Decision 3: Is email provided?
    if email:
        # Decision 4: Does email already exist?
        existing_emails = get_person_emails(pco, person['id'])
        email_exists = any(e['address'] == email for e in existing_emails)
        
        if not email_exists:
            add_email_to_person(pco, person['id'], email, email_location)
    
    return person
```

### Step 2: Design Test Cases

#### Critical Path Tests (6 tests)

1. **Create new person (no email)**
   - Person not found → Create → Return

2. **Create new person with email**
   - Person not found → Create → Add email → Return

3. **Update existing person (attributes changed)**
   - Person found → Attributes differ → Update → Return

4. **Update existing person (no changes)**
   - Person found → Attributes same → Skip update → Return

5. **Add email to existing person**
   - Person found → Email provided → Email new → Add → Return

6. **Skip existing email**
   - Person found → Email provided → Email exists → Skip → Return

#### Edge Case Tests (3 tests)

7. **Create fails, return None**
   - Person not found → Create fails → Return None

8. **Update with partial data**
   - Person found → Only gender provided → Update gender only

9. **Multiple emails exist**
   - Person found → Check against multiple existing emails

### Step 3: Implement Tests

```python
class TestCreateOrUpdatePerson:
    """Tests for create_or_update_person function"""
    
    def test_create_new_person(self, mock_pco_client):
        """Test creating a new person when they don't exist"""
        # Arrange
        mock_pco_client.iterate.return_value = []  # Person not found
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.post.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = create_or_update_person(mock_pco_client, "John", "Doe", "Male")
        
        # Assert
        assert result is not None
        assert result['id'] == '12345'
        mock_pco_client.post.assert_called_once()
    
    def test_update_existing_person(self, mock_pco_client):
        """Test updating an existing person"""
        # Arrange
        existing_person = create_mock_person('12345', 'John', 'Doe', gender='Male')
        mock_pco_client.iterate.return_value = [existing_person]
        mock_pco_client.template.return_value = {'data': {'type': 'Person'}}
        mock_pco_client.patch.return_value = MOCK_PERSON_RESPONSE
        
        # Act
        result = create_or_update_person(mock_pco_client, "John", "Doe", "Female")
        
        # Assert
        assert result is not None
        mock_pco_client.patch.assert_called_once()
    
    # ... more tests following the same pattern
```

---

## Key Principles

### 1. **Test Independence**
Each test should be completely independent:
- ✅ Can run in any order
- ✅ Doesn't depend on other tests
- ✅ Has its own setup and teardown

### 2. **Clear Test Names**
Use descriptive names that explain what's being tested:
- ✅ `test_create_person_with_valid_data()`
- ❌ `test_person_1()`

### 3. **Arrange-Act-Assert Pattern**
Structure every test consistently:
```python
def test_example():
    # Arrange - Set up test data
    mock_data = create_mock()
    
    # Act - Execute the function
    result = function_under_test(mock_data)
    
    # Assert - Verify the results
    assert result == expected_value
```

### 4. **One Concept Per Test**
Each test should verify one specific behavior:
- ✅ `test_create_person_success()`
- ✅ `test_create_person_duplicate_error()`
- ❌ `test_create_and_update_and_delete_person()`

### 5. **Mock External Dependencies**
Never make real API calls in unit tests:
```python
@patch('src.pco_helpers.pypco.PCO')
def test_with_mock(mock_pco):
    # Test with mocked API
```

---

## Handling Complex Scenarios

### Scenario 1: Multiple Dependencies

**Problem**: Function depends on 3+ external services

**Solution**: Mock each dependency separately
```python
@patch('module.service_a')
@patch('module.service_b')
@patch('module.service_c')
def test_complex_function(mock_c, mock_b, mock_a):
    # Configure each mock
    mock_a.return_value = data_a
    mock_b.return_value = data_b
    mock_c.return_value = data_c
    
    # Test the function
    result = complex_function()
    
    # Verify interactions
    mock_a.assert_called_once()
    mock_b.assert_called_once()
    mock_c.assert_called_once()
```

### Scenario 2: Asynchronous Operations

**Problem**: Function has async operations or callbacks

**Solution**: Use pytest-asyncio or mock callbacks
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Scenario 3: State-Dependent Behavior

**Problem**: Function behavior depends on system state

**Solution**: Use fixtures to set up different states
```python
@pytest.fixture
def empty_database():
    # Setup empty state
    yield
    # Cleanup

@pytest.fixture
def populated_database():
    # Setup populated state
    yield
    # Cleanup

def test_with_empty_db(empty_database):
    # Test behavior with empty state

def test_with_data(populated_database):
    # Test behavior with populated state
```

---

## Measuring Success

### Quantitative Metrics
- ✅ **Code Coverage**: 80%+ for critical paths
- ✅ **Test Execution Time**: < 30 seconds for unit tests
- ✅ **Test Count**: Proportional to code complexity
- ✅ **Pass Rate**: 100% on main branch

### Qualitative Metrics
- ✅ **Confidence**: Can refactor without fear
- ✅ **Clarity**: Tests serve as documentation
- ✅ **Maintainability**: Easy to update tests
- ✅ **Completeness**: All critical paths covered

---

## Common Pitfalls to Avoid

### 1. **Over-Testing**
❌ Testing implementation details
✅ Testing behavior and outcomes

### 2. **Under-Testing**
❌ Only testing happy paths
✅ Including error and edge cases

### 3. **Brittle Tests**
❌ Tests break with minor code changes
✅ Tests focus on behavior, not implementation

### 4. **Slow Tests**
❌ Making real API calls in unit tests
✅ Using mocks for external dependencies

### 5. **Unclear Tests**
❌ Complex test logic that's hard to understand
✅ Simple, clear test structure

---

## Continuous Improvement

### Regular Review
- Review test coverage monthly
- Update tests when code changes
- Remove obsolete tests
- Refactor duplicate test code

### Team Practices
- Require tests for new features
- Review tests in code reviews
- Share testing patterns
- Document complex test scenarios

### Automation
- Run tests on every commit (CI/CD)
- Generate coverage reports automatically
- Alert on coverage drops
- Track test metrics over time

---

## Conclusion

Effective testing of complex workflows requires:

1. **Systematic decomposition** of the problem
2. **Strategic test design** covering critical paths
3. **Efficient implementation** avoiding duplication
4. **Continuous verification** of coverage
5. **Regular maintenance** and improvement

By following this methodology, you can confidently tackle even the most complex testing scenarios while maintaining a clean, maintainable test suite.

---

**Remember**: The goal isn't to test everything—it's to test the right things effectively.

---

**Last Updated**: 2025-11-22  
**Version**: 1.0.0