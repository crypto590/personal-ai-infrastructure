---
name: react-component-creator
description: Use this skill when creating, modifying, or optimizing React components and applications. This includes writing new React components, refactoring existing code, implementing React hooks, managing state, handling component lifecycle, optimizing performance, and following modern React best practices. The skill is particularly useful for tasks involving functional components, hooks patterns, custom hooks, and modern React features like concurrent rendering.
---

# React Component Creator

## Overview

This skill provides comprehensive guidance for creating high-quality, production-ready React components following modern best practices. Use it when building new React components, refactoring existing code, implementing custom hooks, or optimizing React applications for performance and maintainability.

## When to Use This Skill

Invoke this skill for:
- Creating new React functional components from scratch
- Implementing React hooks (useState, useEffect, useContext, etc.)
- Building custom hooks for reusable logic
- Refactoring class components to functional components
- Optimizing component performance
- Managing component state and lifecycle
- Implementing proper data fetching patterns
- Following React purity and immutability principles
- Addressing React-specific bugs or anti-patterns

## Core Principles

Before implementing any React component, adhere to these fundamental principles:

1. **Components are pure functions** - Same props always produce the same output
2. **Never mutate props or state** - Always create new objects/arrays
3. **Hooks follow strict rules** - Top-level only, consistent order, no conditional calls
4. **Components defined at module level** - Never create components inside other components
5. **Immutability throughout** - No mutations after values are passed to JSX or hooks
6. **TypeScript by default** - All components should use TypeScript for type safety
7. **Server vs Client components** - In Next.js App Router, prefer Server Components by default; use "use client" directive only when needed

## Component Creation Workflow

### 1. Plan Component Structure

Before writing code, determine:
- Is this a Server Component or Client Component? (Next.js App Router)
- Is this a presentational or container component?
- What props does it need? (Define TypeScript interface)
- What local state is required?
- What side effects need to be managed?
- Are custom hooks needed for reusable logic?
- Does it need error boundaries?

### 2. Write the Component

Follow this template structure for functional components:

#### Client Component (TypeScript)

```typescript
'use client'; // Only if component uses hooks, browser APIs, or event handlers

import { useState, useEffect, useCallback, useMemo } from 'react';

interface ComponentNameProps {
  prop1: string;
  prop2: number;
}

export function ComponentName({ prop1, prop2 }: ComponentNameProps) {
  // 1. All hooks at the top level (never conditional)
  const [state, setState] = useState<string>(initialValue);
  const contextValue = useContext(SomeContext);

  // 2. Derived values and memoization
  const derivedValue = useMemo(() => {
    return expensiveComputation(prop1, prop2);
  }, [prop1, prop2]);

  // 3. Event handlers and callbacks
  const handleClick = useCallback(() => {
    setState(newValue);
  }, []);

  // 4. Effects (for synchronization only)
  useEffect(() => {
    // Setup
    const subscription = subscribe();

    // Cleanup
    return () => subscription.unsubscribe();
  }, [dependencies]);

  // 5. Early returns (after all hooks)
  if (loading) return <Loading />;
  if (error) return <Error message={error} />;

  // 6. Render JSX
  return (
    <div>
      <button onClick={handleClick}>
        {derivedValue}
      </button>
    </div>
  );
}
```

#### Server Component (TypeScript - Next.js App Router)

```typescript
// No 'use client' directive - Server Component by default

interface UserProfileProps {
  userId: string;
}

export async function UserProfile({ userId }: UserProfileProps) {
  // Server Components can be async and fetch data directly
  const user = await fetch(`https://api.example.com/users/${userId}`)
    .then(res => res.json());

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

### 3. Validate Against Best Practices

Check the component against these criteria:
- All hooks are called at the top level
- No hooks after early returns or in conditionals
- State is never mutated directly
- Dependencies in useEffect/useCallback/useMemo are complete
- Event handlers are properly defined
- Props are not mutated
- Component is defined at module level (not inside another component)

### 4. Optimize if Needed

Apply optimizations only after measuring performance:
- Wrap expensive computations in `useMemo`
- Wrap callback functions in `useCallback` when passed to memoized children
- Use `React.memo` for components that re-render unnecessarily
- Consider code splitting for large components

## Next.js App Router Specifics

### Server vs Client Components

**Server Components (Default):**
- No "use client" directive needed
- Can be async functions
- Can fetch data directly with await
- Rendered on the server
- Cannot use hooks, event handlers, or browser APIs
- Smaller JavaScript bundle

**Client Components:**
- Require "use client" directive at the top of the file
- Can use hooks (useState, useEffect, etc.)
- Can use event handlers (onClick, onChange, etc.)
- Can access browser APIs (window, localStorage, etc.)
- Rendered on both server (initial) and client (hydration)

```typescript
// Server Component - prefer by default
export async function BlogPost({ slug }: { slug: string }) {
  const post = await fetch(`https://api.example.com/posts/${slug}`)
    .then(res => res.json());

  return <article>{post.content}</article>;
}

// Client Component - only when needed
'use client';

export function LikeButton({ postId }: { postId: string }) {
  const [liked, setLiked] = useState(false);

  return (
    <button onClick={() => setLiked(!liked)}>
      {liked ? '❤️' : '🤍'}
    </button>
  );
}
```

### Composition Pattern

Combine Server and Client Components effectively:

```typescript
// app/blog/[slug]/page.tsx (Server Component)
import { LikeButton } from '@/components/LikeButton';

export default async function BlogPage({ params }: { params: { slug: string } }) {
  const post = await fetch(`https://api.example.com/posts/${params.slug}`)
    .then(res => res.json());

  return (
    <article>
      <h1>{post.title}</h1>
      <div>{post.content}</div>
      <LikeButton postId={post.id} /> {/* Client Component */}
    </article>
  );
}
```

## Common Tasks

### Creating a Form Component (TypeScript)

```typescript
'use client';

import { useState } from 'react';

interface LoginFormProps {
  onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      await login(email, password);
      onSuccess?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        disabled={isLoading}
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        disabled={isLoading}
        required
      />
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={isLoading}>
        {isLoading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Creating a Custom Hook (TypeScript)

Extract reusable logic into custom hooks. Always prefix with "use":

```typescript
'use client';

import { useState, useCallback, ChangeEvent } from 'react';

interface UseFormInputReturn {
  value: string;
  onChange: (e: ChangeEvent<HTMLInputElement>) => void;
  reset: () => void;
}

function useFormInput(initialValue: string): UseFormInputReturn {
  const [value, setValue] = useState(initialValue);

  const handleChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
  }, []);

  const reset = useCallback(() => {
    setValue(initialValue);
  }, [initialValue]);

  return {
    value,
    onChange: handleChange,
    reset
  };
}

// Usage in component
export function RegistrationForm() {
  const emailInput = useFormInput('');
  const passwordInput = useFormInput('');

  return (
    <form>
      <input type="email" {...emailInput} />
      <input type="password" {...passwordInput} />
    </form>
  );
}
```

### Data Fetching Patterns

#### Option 1: Server Component (Preferred for Next.js App Router)

```typescript
// No 'use client' - Server Component
interface User {
  id: string;
  name: string;
  email: string;
}

interface UserProfileProps {
  userId: string;
}

export async function UserProfile({ userId }: UserProfileProps) {
  // Direct async/await in Server Component
  const user: User = await fetch(`https://api.example.com/users/${userId}`, {
    next: { revalidate: 3600 } // Cache for 1 hour
  }).then(res => {
    if (!res.ok) throw new Error('Failed to fetch user');
    return res.json();
  });

  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

#### Option 2: Client Component with `use` Hook (React 19)

```typescript
'use client';

import { use, Suspense } from 'react';

interface User {
  id: string;
  name: string;
}

async function fetchUser(userId: string): Promise<User> {
  const res = await fetch(`/api/users/${userId}`);
  if (!res.ok) throw new Error('Failed to fetch');
  return res.json();
}

interface UserProfileProps {
  userId: string;
}

function UserProfile({ userId }: UserProfileProps) {
  // React 19 'use' hook - unwraps promises
  const user = use(fetchUser(userId));

  return (
    <div>
      <h1>{user.name}</h1>
    </div>
  );
}

// Wrap with Suspense boundary
export function UserProfileWithSuspense({ userId }: UserProfileProps) {
  return (
    <Suspense fallback={<Loading />}>
      <UserProfile userId={userId} />
    </Suspense>
  );
}
```

#### Option 3: Client Component with useEffect (Legacy Pattern)

```typescript
'use client';

import { useState, useEffect } from 'react';

interface User {
  id: string;
  name: string;
}

interface UseDataReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

function useData<T>(url: string | null): UseDataReturn<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!url) return;

    let ignore = false;
    setLoading(true);

    fetch(url)
      .then(response => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
      })
      .then(json => {
        if (!ignore) {
          setData(json);
          setError(null);
        }
      })
      .catch(err => {
        if (!ignore) {
          setError(err instanceof Error ? err.message : 'An error occurred');
        }
      })
      .finally(() => {
        if (!ignore) {
          setLoading(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [url]);

  return { data, loading, error };
}

// Usage
export function UserProfile({ userId }: { userId: string }) {
  const { data: user, loading, error } = useData<User>(`/api/users/${userId}`);

  if (loading) return <Loading />;
  if (error) return <Error message={error} />;
  if (!user) return null;

  return <div>{user.name}</div>;
}
```

### Context and State Management (TypeScript)

Implement context with custom hooks for clean access:

```typescript
'use client';

import { createContext, useContext, useState, useCallback, useMemo, ReactNode } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserDispatch {
  login: (userData: User) => void;
  logout: () => void;
}

const UserContext = createContext<User | null>(null);
const UserDispatchContext = createContext<UserDispatch | null>(null);

// Custom hooks for context access
export function useUser() {
  const context = useContext(UserContext);
  if (context === null) {
    throw new Error('useUser must be used within UserProvider');
  }
  return context;
}

export function useUserDispatch() {
  const context = useContext(UserDispatchContext);
  if (context === null) {
    throw new Error('useUserDispatch must be used within UserProvider');
  }
  return context;
}

// Provider component
export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = useCallback((userData: User) => {
    setUser(userData);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
  }, []);

  const dispatch = useMemo(() => ({ login, logout }), [login, logout]);

  return (
    <UserContext.Provider value={user}>
      <UserDispatchContext.Provider value={dispatch}>
        {children}
      </UserDispatchContext.Provider>
    </UserContext.Provider>
  );
}

// Usage in components
export function UserMenu() {
  const user = useUser();
  const { logout } = useUserDispatch();

  return (
    <div>
      <span>{user.name}</span>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### List Rendering with Keys

Always use proper keys for list items:

```javascript
function TodoList({ todos }) {
  return (
    <ul>
      {todos.map(todo => (
        <TodoItem
          key={todo.id}  // Use stable, unique ID
          todo={todo}
        />
      ))}
    </ul>
  );
}

// Managing list state immutably
function TodoApp() {
  const [todos, setTodos] = useState([]);

  const addTodo = (text) => {
    const newTodo = { id: crypto.randomUUID(), text, completed: false };
    setTodos([...todos, newTodo]);
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const removeTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  return (
    <div>
      <TodoInput onAdd={addTodo} />
      <TodoList
        todos={todos}
        onToggle={toggleTodo}
        onRemove={removeTodo}
      />
    </div>
  );
}
```

### Error Handling

#### Error Boundaries (Class Component - Required for now)

```typescript
'use client';

import { Component, ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div role="alert">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
export function App() {
  return (
    <ErrorBoundary fallback={<ErrorFallback />}>
      <MyComponent />
    </ErrorBoundary>
  );
}
```

#### Throwing Errors in Render (React 19 Pattern)

```typescript
// Server Component - can throw directly
export async function UserProfile({ userId }: { userId: string }) {
  const res = await fetch(`/api/users/${userId}`);

  if (!res.ok) {
    // Throwing in Server Component will be caught by nearest error.tsx
    throw new Error('Failed to load user');
  }

  const user = await res.json();
  return <div>{user.name}</div>;
}

// Client Component with use hook - errors caught by Suspense boundary
'use client';

import { use, Suspense } from 'react';

function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Errors throw and bubble up
  return <div>{user.name}</div>;
}

export function UserProfileWrapper({ userId }: { userId: string }) {
  const userPromise = fetchUser(userId);

  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <UserProfile userPromise={userPromise} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Testing Components

#### Vitest + Testing Library Setup

```typescript
// Button.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

#### Testing Custom Hooks

```typescript
// useCounter.test.ts
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter(0));
    expect(result.current.count).toBe(0);
  });

  it('increments counter', () => {
    const { result } = renderHook(() => useCounter(0));

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it('decrements counter', () => {
    const { result } = renderHook(() => useCounter(5));

    act(() => {
      result.current.decrement();
    });

    expect(result.current.count).toBe(4);
  });
});
```

#### Testing Components with Context

```typescript
// UserMenu.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { UserProvider } from './UserContext';
import { UserMenu } from './UserMenu';

describe('UserMenu', () => {
  it('displays user name', () => {
    const mockUser = { id: '1', name: 'John Doe', email: 'john@example.com' };

    render(
      <UserProvider initialUser={mockUser}>
        <UserMenu />
      </UserProvider>
    );

    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });

  it('calls logout when logout button clicked', () => {
    const mockLogout = vi.fn();

    render(
      <UserProvider onLogout={mockLogout}>
        <UserMenu />
      </UserProvider>
    );

    fireEvent.click(screen.getByText('Logout'));
    expect(mockLogout).toHaveBeenCalled();
  });
});
```

#### Testing Async Components (Server Components)

```typescript
// UserProfile.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

// Mock fetch
global.fetch = vi.fn();

describe('UserProfile', () => {
  it('renders user data', async () => {
    const mockUser = { id: '1', name: 'Jane Doe', email: 'jane@example.com' };

    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser,
    });

    render(await UserProfile({ userId: '1' }));

    expect(screen.getByText('Jane Doe')).toBeInTheDocument();
    expect(screen.getByText('jane@example.com')).toBeInTheDocument();
  });

  it('handles fetch errors', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
    });

    await expect(async () => {
      render(await UserProfile({ userId: '1' }));
    }).rejects.toThrow('Failed to fetch user');
  });
});
```

## Critical Anti-Patterns to Avoid

### 1. Never Call Hooks Conditionally

```javascript
// ❌ WRONG
function Component({ isLoggedIn }) {
  if (isLoggedIn) {
    const [user, setUser] = useState(null);
  }
  return <div>...</div>;
}

// ✅ CORRECT
function Component({ isLoggedIn }) {
  const [user, setUser] = useState(null);

  if (!isLoggedIn) return <Login />;

  return <div>{user.name}</div>;
}
```

### 2. Never Mutate State or Props

```javascript
// ❌ WRONG
function TodoList({ todos }) {
  const addTodo = (text) => {
    todos.push({ text }); // Mutation!
    setTodos(todos);
  };
}

// ✅ CORRECT
function TodoList() {
  const [todos, setTodos] = useState([]);

  const addTodo = (text) => {
    setTodos([...todos, { text }]); // New array
  };
}
```

### 3. Never Define Components Inside Components

```javascript
// ❌ WRONG
function Parent() {
  function Child() {  // Re-created every render!
    return <div>Child</div>;
  }
  return <Child />;
}

// ✅ CORRECT
function Child() {
  return <div>Child</div>;
}

function Parent() {
  return <Child />;
}
```

### 4. Never Pass Hooks as Props

```javascript
// ❌ WRONG
function Button({ useData }) {
  const data = useData(); // Don't pass hooks as props
  return <button>{data}</button>;
}

// ✅ CORRECT
function Button() {
  const data = useData(); // Call hooks directly
  return <button>{data}</button>;
}
```

### 5. Don't Use Effect for Derived State

```javascript
// ❌ WRONG
function Component({ firstName, lastName }) {
  const [fullName, setFullName] = useState('');

  useEffect(() => {
    setFullName(`${firstName} ${lastName}`);
  }, [firstName, lastName]);

  return <div>{fullName}</div>;
}

// ✅ CORRECT
function Component({ firstName, lastName }) {
  const fullName = `${firstName} ${lastName}`; // Derive during render
  return <div>{fullName}</div>;
}
```

## Performance Optimization

### Measure Before Optimizing

Use React DevTools Profiler to identify actual performance issues. Don't prematurely optimize.

### Memoization Techniques

```javascript
// Memoize expensive computations
function ProductList({ products, category }) {
  const filteredProducts = useMemo(() => {
    return products.filter(p => p.category === category);
  }, [products, category]);

  return (
    <div>
      {filteredProducts.map(product => (
        <Product key={product.id} product={product} />
      ))}
    </div>
  );
}

// Memoize callbacks passed to children
function Parent() {
  const [count, setCount] = useState(0);

  const handleClick = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  return <MemoizedChild onClick={handleClick} />;
}

// Memoize components
const MemoizedChild = React.memo(function Child({ onClick }) {
  return <button onClick={onClick}>Click me</button>;
});
```

## Reference Documentation

For comprehensive details on React best practices, patterns, and anti-patterns, refer to:
- `references/react_best_practices.md` - Complete guide covering hooks, component patterns, purity, immutability, custom hooks, and modern React features

Load this reference when:
- Implementing complex custom hooks
- Debugging React-specific issues
- Reviewing code for anti-patterns
- Learning advanced patterns like context, reducers, or concurrent features
- Optimizing performance

## Implementation Checklist

When creating or reviewing React components, verify:

**TypeScript & Types:**
- [ ] Component uses TypeScript (.tsx extension)
- [ ] Props interface defined with clear types
- [ ] Generic types used for reusable components/hooks
- [ ] Return types specified for functions
- [ ] No `any` types unless absolutely necessary

**Next.js App Router (if applicable):**
- [ ] Server Component by default (no 'use client' unless needed)
- [ ] 'use client' directive only when using hooks, events, or browser APIs
- [ ] Async Server Components for data fetching (not useEffect)
- [ ] Proper error.tsx boundaries for error handling
- [ ] Loading.tsx or Suspense for loading states

**Component Structure:**
- [ ] Component defined at module level (not inside another component)
- [ ] All hooks called at top level (no conditionals, loops, or early returns before hooks)
- [ ] Hooks called in consistent order every render
- [ ] Component is pure (same props → same output)

**State & Props:**
- [ ] State never mutated directly (always use setState with new values)
- [ ] Props never mutated
- [ ] No mutations after values passed to JSX
- [ ] Derived state calculated during render (not in useEffect)

**Hooks:**
- [ ] useEffect includes all dependencies
- [ ] useEffect returns cleanup function when needed
- [ ] Custom hooks prefixed with "use"
- [ ] Custom hooks follow Rules of Hooks
- [ ] No hooks passed as props
- [ ] Consider `use` hook for promises (React 19)

**Rendering:**
- [ ] Event handlers properly defined and named
- [ ] Keys used correctly in list rendering (stable, unique IDs)
- [ ] Error boundaries wrap components that may throw

**Performance:**
- [ ] Performance optimizations only applied after measuring
- [ ] useMemo/useCallback used appropriately (not prematurely)

**Testing:**
- [ ] Component has test coverage (Vitest + Testing Library)
- [ ] Tests cover main user interactions
- [ ] Tests verify accessibility (roles, labels)

## Common Debugging Steps

When encountering React issues:

1. **"You're importing a component that needs X" error**: Add 'use client' directive - component uses hooks or browser APIs
2. **State not updating**: Check for direct mutations, verify setState is called with new values
3. **Infinite re-renders**: Check useEffect dependencies, verify state updates aren't unconditional
4. **Stale closures**: Ensure dependencies are complete in useCallback/useMemo/useEffect
5. **Hook errors**: Verify hooks are at top level, not conditional
6. **Component not re-rendering**: Check if props/state are actually changing (reference equality)
7. **Memory leaks**: Ensure useEffect cleanup functions properly cancel subscriptions
8. **Server Component async issues**: Ensure component is not marked with 'use client' if using async/await
9. **TypeScript errors**: Verify props interface matches usage, check generic type parameters
10. **Hydration mismatches**: Ensure Server and Client Components render the same initial HTML
