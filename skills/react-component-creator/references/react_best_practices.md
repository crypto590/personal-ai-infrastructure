# React Modern Best Practices Reference

This document provides comprehensive guidance on modern React best practices, patterns, and anti-patterns based on the latest React documentation. All examples use TypeScript and follow Next.js App Router conventions where applicable.

## Component Structure

### Functional Components
All components should be functional components using hooks with TypeScript. Class components are legacy (except for Error Boundaries which still require classes).

```typescript
// ✅ Good: Functional component with TypeScript
interface UserProfileProps {
  userId: string;
}

export function UserProfile({ userId }: UserProfileProps) {
  const [user, setUser] = useState<User | null>(null);
  return <div>{user?.name}</div>;
}

// ❌ Avoid: Class components (legacy)
class UserProfile extends React.Component {
  // ...
}
```

### TypeScript Best Practices
- Always define prop interfaces
- Use explicit types for state
- Avoid `any` types
- Use generics for reusable components

```typescript
// ✅ Good: Explicit types
interface ButtonProps {
  variant: 'primary' | 'secondary';
  onClick: () => void;
  children: ReactNode;
  disabled?: boolean;
}

export function Button({ variant, onClick, children, disabled = false }: ButtonProps) {
  return (
    <button onClick={onClick} disabled={disabled} className={variant}>
      {children}
    </button>
  );
}

// ✅ Good: Generic components
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => ReactNode;
  keyExtractor: (item: T) => string;
}

export function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
  return (
    <ul>
      {items.map(item => (
        <li key={keyExtractor(item)}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}
```

### Component Definition Rules
- Define components at the module level, never inside other components
- Avoid factory functions that create components
- Components should be stable across renders

```typescript
// ✅ Good: Component defined at module level
interface ButtonProps {
  color: string;
  children: ReactNode;
}

export function Button({ color, children }: ButtonProps) {
  return <button style={{ backgroundColor: color }}>{children}</button>;
}

export function App() {
  return <Button color="red">Click me</Button>;
}

// ❌ Bad: Component defined inside another component
function Parent() {
  function Child() {  // Re-created on every render!
    return <div>Child</div>;
  }
  return <Child />;
}

// ❌ Bad: Factory function creating components
function createComponent(defaultValue: string) {
  return function Component() {
    // ...
  };
}
```

## Next.js Server Components (App Router)

### Server vs Client Components

**Server Components (Default):**
- Can be async functions
- Fetch data directly with await
- No hooks, event handlers, or browser APIs
- Smaller bundle size
- Better SEO and initial load

**Client Components:**
- Require 'use client' directive
- Can use hooks and browser APIs
- Handle interactivity and state

```typescript
// ✅ Server Component (default)
interface Post {
  id: string;
  title: string;
  content: string;
}

interface BlogPostProps {
  postId: string;
}

export async function BlogPost({ postId }: BlogPostProps) {
  // Direct data fetching in Server Component
  const post: Post = await fetch(`https://api.example.com/posts/${postId}`, {
    next: { revalidate: 3600 } // ISR: revalidate every hour
  }).then(res => res.json());

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}

// ✅ Client Component (when needed)
'use client';

interface LikeButtonProps {
  postId: string;
  initialLikes: number;
}

export function LikeButton({ postId, initialLikes }: LikeButtonProps) {
  const [likes, setLikes] = useState(initialLikes);
  const [isLiked, setIsLiked] = useState(false);

  const handleLike = async () => {
    setIsLiked(!isLiked);
    setLikes(isLiked ? likes - 1 : likes + 1);
    await fetch(`/api/posts/${postId}/like`, { method: 'POST' });
  };

  return (
    <button onClick={handleLike}>
      {isLiked ? '❤️' : '🤍'} {likes}
    </button>
  );
}
```

### Composing Server and Client Components

```typescript
// app/posts/[id]/page.tsx (Server Component)
import { LikeButton } from '@/components/LikeButton';
import { Comments } from '@/components/Comments';

export default async function PostPage({ params }: { params: { id: string } }) {
  const [post, comments] = await Promise.all([
    fetch(`https://api.example.com/posts/${params.id}`).then(res => res.json()),
    fetch(`https://api.example.com/posts/${params.id}/comments`).then(res => res.json())
  ]);

  return (
    <div>
      <h1>{post.title}</h1>
      <p>{post.content}</p>

      {/* Client Component for interactivity */}
      <LikeButton postId={post.id} initialLikes={post.likes} />

      {/* Can pass server-fetched data to client components */}
      <Comments comments={comments} postId={post.id} />
    </div>
  );
}
```

## React 19 Features

### The `use` Hook

The `use` hook unwraps promises and context values. Unlike other hooks, it can be called conditionally.

```typescript
'use client';

import { use, Suspense } from 'react';

interface User {
  id: string;
  name: string;
  email: string;
}

// ✅ Using the use hook with promises
function UserProfile({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise); // Unwraps the promise

  return (
    <div>
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  );
}

// Wrap with Suspense
export function UserProfilePage({ userId }: { userId: string }) {
  const userPromise = fetch(`/api/users/${userId}`).then(res => res.json());

  return (
    <Suspense fallback={<div>Loading user...</div>}>
      <UserProfile userPromise={userPromise} />
    </Suspense>
  );
}

// ✅ Conditional use of the use hook (unique to this hook!)
function Message({ messagePromise, showMessage }: {
  messagePromise: Promise<string>;
  showMessage: boolean;
}) {
  if (!showMessage) {
    return null;
  }

  const message = use(messagePromise); // Can be conditional!
  return <p>{message}</p>;
}
```

### Error Handling with use Hook

```typescript
'use client';

import { use, Suspense } from 'react';

function DataDisplay({ dataPromise }: { dataPromise: Promise<Data> }) {
  const data = use(dataPromise); // Errors bubble to nearest ErrorBoundary
  return <div>{data.value}</div>;
}

export function DataPage() {
  const dataPromise = fetchData();

  return (
    <ErrorBoundary fallback={<ErrorUI />}>
      <Suspense fallback={<Loading />}>
        <DataDisplay dataPromise={dataPromise} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

## Hooks Best Practices

### Rules of Hooks
1. Only call hooks at the top level of function components or custom hooks
2. Never call hooks conditionally, in loops, or after early returns
3. Hook calls must be in the same order on every render

```typescript
// ✅ Good: Hooks at top level
interface ComponentProps {
  isSpecial: boolean;
}

function Component({ isSpecial }: ComponentProps) {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('');

  if (!isSpecial) {
    return null;
  }

  return <div>{name}: {count}</div>;
}

// ❌ Bad: Conditional hook
function Component({ isLoggedIn }: { isLoggedIn: boolean }) {
  if (isLoggedIn) {
    const [user, setUser] = useState<User | null>(null); // Violates Rules of Hooks!
  }
  return <div>...</div>;
}

// ❌ Bad: Hook after early return
function Component({ data }: { data: string | null }) {
  if (!data) return <Loading />;
  const [processed, setProcessed] = useState(data); // Never called when data is null!
  return <div>{processed}</div>;
}

// ❌ Bad: Hook in callback
function Component() {
  return (
    <button onClick={() => {
      const [clicked, setClicked] = useState(false); // Hooks can't be in event handlers!
    }}>
      Click
    </button>
  );
}
```

### useState Hook
- Use for local component state
- State setter functions can accept updater functions for atomic updates
- Multiple useState calls are better than complex state objects for unrelated data

```javascript
// ✅ Good: Separate state for independent values
function Form() {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  // ...
}

// ✅ Good: Updater function for state based on previous state
function Counter() {
  const [count, setCount] = useState(0);

  const increment = () => {
    setCount(c => c + 1); // Uses previous value
  };

  return <button onClick={increment}>{count}</button>;
}
```

### useEffect Hook
- Use for synchronization with external systems (APIs, subscriptions, DOM)
- Always return cleanup functions when needed
- Specify all dependencies in the dependency array
- Separate unrelated effects into different useEffect calls

```javascript
// ✅ Good: Separate effects for separate concerns
function ChatRoom({ roomId }) {
  useEffect(() => {
    logVisit(roomId);
  }, [roomId]);

  useEffect(() => {
    const connection = createConnection(serverUrl, roomId);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId]);

  // ...
}

// ✅ Good: Cleanup function for subscriptions
useEffect(() => {
  const subscription = subscribe(callback);
  return () => subscription.unsubscribe();
}, [callback]);

// ❌ Avoid: Multiple concerns in one effect
useEffect(() => {
  logVisit(roomId);
  const connection = createConnection(serverUrl, roomId);
  connection.connect();
  return () => connection.disconnect();
}, [roomId]); // Mixes analytics and connection logic
```

### useContext Hook
- Use for accessing context values
- Wrap context access in custom hooks for better ergonomics
- Context providers should be at appropriate levels in the tree

```javascript
// ✅ Good: Custom hooks for context access
export function useTasks() {
  return useContext(TasksContext);
}

export function useTasksDispatch() {
  return useContext(TasksDispatchContext);
}

// Usage in components
function TaskList() {
  const tasks = useTasks();
  const dispatch = useTasksDispatch();
  // ...
}
```

### useCallback Hook
- Use to memoize callback functions
- Essential when passing callbacks to optimized child components
- Custom hooks should wrap returned functions in useCallback

```javascript
// ✅ Good: Memoize callbacks in custom hooks
function useRouter() {
  const { dispatch } = useContext(RouterStateContext);

  const navigate = useCallback((url) => {
    dispatch({ type: 'navigate', url });
  }, [dispatch]);

  const goBack = useCallback(() => {
    dispatch({ type: 'back' });
  }, [dispatch]);

  return { navigate, goBack };
}
```

### useMemo Hook
- Use to memoize expensive computations
- Helps optimize performance when combined with immutable arguments

```javascript
// ✅ Good: Memoize expensive computations
function useIconStyle(icon) {
  const theme = useContext(ThemeContext);

  return useMemo(() => {
    const newIcon = { ...icon };
    if (newIcon.enabled) {
      newIcon.className = computeStyle(newIcon, theme);
    }
    return newIcon;
  }, [icon, theme]);
}
```

## Custom Hooks

### Purpose and Naming
- Extract reusable stateful logic into custom hooks
- Always prefix custom hooks with "use"
- Custom hooks enable logic sharing without component hierarchy changes

```javascript
// ✅ Good: Custom hook for form input logic
function useFormInput(initialValue) {
  const [value, setValue] = useState(initialValue);

  const handleChange = (e) => {
    setValue(e.target.value);
  };

  return {
    value,
    onChange: handleChange
  };
}

// Usage
function Form() {
  const firstNameProps = useFormInput('Mary');
  const lastNameProps = useFormInput('Poppins');

  return (
    <>
      <input {...firstNameProps} />
      <input {...lastNameProps} />
    </>
  );
}
```

### Custom Hook Best Practices
- Never pass hooks as props or create higher-order hooks
- Don't mutate hook arguments
- Avoid custom "lifecycle" hooks that just wrap useEffect
- Return stable function references with useCallback

```javascript
// ❌ Bad: Don't pass hooks as props
function ChatInput() {
  return <Button useData={useDataWithLogging} />
}

// ✅ Good: Call hooks directly where needed
function ChatInput() {
  return <Button />
}

function Button() {
  const data = useDataWithLogging();
  // ...
}

// ❌ Bad: Custom lifecycle hooks
function useMount(fn) {
  useEffect(() => {
    fn();
  }, []); // Missing dependency: fn
}

// ✅ Good: Use useEffect directly with proper dependencies
function ChatRoom({ roomId }) {
  useEffect(() => {
    const connection = createConnection(roomId);
    connection.connect();
    return () => connection.disconnect();
  }, [roomId]);
}

// ❌ Bad: Don't mutate hook arguments
function useIconStyle(icon) {
  const theme = useContext(ThemeContext);
  if (icon.enabled) {
    icon.className = computeStyle(icon, theme); // Mutation!
  }
  return icon;
}

// ✅ Good: Create new objects instead
function useIconStyle(icon) {
  const theme = useContext(ThemeContext);
  const newIcon = { ...icon };
  if (newIcon.enabled) {
    newIcon.className = computeStyle(newIcon, theme);
  }
  return newIcon;
}
```

### Common Custom Hook Patterns

#### Data Fetching Hook
```javascript
function useData(url) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!url) return;

    let ignore = false;
    fetch(url)
      .then(response => response.json())
      .then(json => {
        if (!ignore) {
          setData(json);
        }
      });

    return () => {
      ignore = true;
    };
  }, [url]);

  return data;
}

// Usage
function ShippingForm({ country }) {
  const cities = useData(`/api/cities?country=${country}`);
  const [city, setCity] = useState(null);
  const areas = useData(city ? `/api/areas?city=${city}` : null);
  // ...
}
```

#### External Store Subscription Hook
```javascript
function useOnlineStatus() {
  const isOnline = useSyncExternalStore(subscribe, getSnapshot);
  return isOnline;
}

function getSnapshot() {
  return navigator.onLine;
}

function subscribe(callback) {
  window.addEventListener('online', callback);
  window.addEventListener('offline', callback);
  return () => {
    window.removeEventListener('online', callback);
    window.removeEventListener('offline', callback);
  };
}
```

## Component Patterns

### Composition Over Hierarchy
- Pass JSX as children for flexibility
- Use render props when children need access to internal state
- Avoid deeply nested prop drilling

```javascript
// ✅ Good: Composition with children
function Card({ children, title }) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}

function App() {
  return (
    <Card title="User Profile">
      <UserAvatar />
      <UserDetails />
    </Card>
  );
}
```

### Event Handlers
- Define event handlers inside the component
- Use arrow functions for handlers that need parameters
- Avoid creating new function references unnecessarily in render

```javascript
function Button() {
  const handleClick = () => {
    console.log('clicked');
  };

  return <button onClick={handleClick}>Click me</button>;
}

// With parameters
function ItemList({ items }) {
  const handleItemClick = (id) => {
    console.log('Item clicked:', id);
  };

  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => handleItemClick(item.id)}>
          {item.name}
        </li>
      ))}
    </ul>
  );
}
```

## Purity and Immutability

### Component Purity
- Components should be pure functions of their props
- Never mutate props or state directly
- Avoid side effects in the render phase

```javascript
// ✅ Good: Pure component
function UserGreeting({ user }) {
  return <h1>Hello, {user.name}!</h1>;
}

// ❌ Bad: Mutating props
function UserGreeting({ user }) {
  user.lastSeen = new Date(); // Never mutate props!
  return <h1>Hello, {user.name}!</h1>;
}
```

### Immutability in State Updates
- Always create new objects/arrays for state updates
- Use spread operators for shallow copies
- Use array methods that return new arrays (map, filter, etc.)

```javascript
// ✅ Good: Immutable state updates
function TodoList() {
  const [todos, setTodos] = useState([]);

  const addTodo = (text) => {
    setTodos([...todos, { id: Date.now(), text }]);
  };

  const removeTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id));
  };

  const toggleTodo = (id) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  // ...
}

// ❌ Bad: Mutating state
function TodoList() {
  const [todos, setTodos] = useState([]);

  const addTodo = (text) => {
    todos.push({ id: Date.now(), text }); // Mutation!
    setTodos(todos); // Won't trigger re-render correctly
  };
}
```

### JSX and Props Immutability
- Never mutate values after passing to JSX
- Create new objects for different props

```javascript
// ✅ Good: Create new objects for different props
function Page({ colour }) {
  const headerStyles = { colour, size: "large" };
  const header = <Header styles={headerStyles} />;
  const footerStyles = { colour, size: "small" };
  const footer = <Footer styles={footerStyles} />;

  return (
    <>
      {header}
      <Content />
      {footer}
    </>
  );
}

// ❌ Bad: Mutating after passing to JSX
function Page({ colour }) {
  const styles = { colour, size: "large" };
  const header = <Header styles={styles} />;
  styles.size = "small"; // Mutation after use in JSX!
  const footer = <Footer styles={styles} />;

  return (
    <>
      {header}
      <Content />
      {footer}
    </>
  );
}
```

## Performance Optimization

### When to Optimize
- Measure before optimizing
- Use React DevTools Profiler
- Focus on slow renders and unnecessary re-renders

### Optimization Techniques
1. **React.memo** - Memoize components to prevent re-renders
2. **useMemo** - Memoize expensive computations
3. **useCallback** - Memoize callback functions
4. **Code splitting** - Lazy load components
5. **Virtualization** - Render only visible items in long lists

```javascript
// Memoized component
const MemoizedComponent = React.memo(function MyComponent({ data }) {
  return <div>{data}</div>;
});

// With custom comparison
const MemoizedComponent = React.memo(
  function MyComponent({ data }) {
    return <div>{data}</div>;
  },
  (prevProps, nextProps) => {
    return prevProps.data.id === nextProps.data.id;
  }
);
```

## Common Anti-Patterns to Avoid

1. **Don't use indexes as keys in lists** (unless list is static and items don't have unique IDs)
2. **Don't call hooks conditionally**
3. **Don't mutate state or props**
4. **Don't create components inside components**
5. **Don't pass hooks as props**
6. **Avoid deeply nested prop drilling** (use context instead)
7. **Don't use useEffect for derived state** (calculate during render instead)
8. **Avoid unnecessary state** (derive from props when possible)

## Modern React Features

### Concurrent Features
- React 18+ supports concurrent rendering
- Use `useTransition` for non-urgent updates
- Use `useDeferredValue` for deferring expensive renders

### Server Components (Next.js, etc.)
- Server Components fetch data on the server
- Reduce client-side JavaScript bundle size
- Better initial page load performance

### Suspense
- Handle loading states declaratively
- Works with lazy loading and data fetching
- Enables better user experiences during async operations

```typescript
// Lazy loading with Suspense
const LazyComponent = React.lazy(() => import('./LazyComponent'));

export function App() {
  return (
    <Suspense fallback={<Loading />}>
      <LazyComponent />
    </Suspense>
  );
}
```

## Error Handling

### Error Boundaries

Error boundaries catch JavaScript errors in child components and display fallback UI. They must be class components (for now).

```typescript
'use client';

import { Component, ReactNode, ErrorInfo } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
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
    this.props.onError?.(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div role="alert">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Error Handling in Server Components

```typescript
// app/posts/[id]/page.tsx
export default async function PostPage({ params }: { params: { id: string } }) {
  const res = await fetch(`https://api.example.com/posts/${params.id}`);

  if (!res.ok) {
    // This will be caught by the nearest error.tsx file
    throw new Error('Failed to load post');
  }

  const post = await res.json();
  return <article>{post.content}</article>;
}

// app/posts/[id]/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

### Error Handling with use Hook

```typescript
'use client';

function DataComponent({ dataPromise }: { dataPromise: Promise<Data> }) {
  // If promise rejects, error bubbles to ErrorBoundary
  const data = use(dataPromise);
  return <div>{data.value}</div>;
}

export function Page() {
  const dataPromise = fetchData();

  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <DataComponent dataPromise={dataPromise} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

## Testing

### Vitest + Testing Library

Testing modern React components with TypeScript.

#### Basic Component Tests

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

  it('applies correct variant class', () => {
    render(<Button variant="primary">Primary</Button>);
    expect(screen.getByRole('button')).toHaveClass('primary');
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

  it('resets to initial value', () => {
    const { result } = renderHook(() => useCounter(10));

    act(() => {
      result.current.increment();
      result.current.increment();
      result.current.reset();
    });

    expect(result.current.count).toBe(10);
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

const mockUser = {
  id: '1',
  name: 'John Doe',
  email: 'john@example.com'
};

describe('UserMenu', () => {
  it('displays user name when logged in', () => {
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
      <UserProvider initialUser={mockUser} onLogout={mockLogout}>
        <UserMenu />
      </UserProvider>
    );

    fireEvent.click(screen.getByText('Logout'));
    expect(mockLogout).toHaveBeenCalled();
  });

  it('shows login button when not logged in', () => {
    render(
      <UserProvider initialUser={null}>
        <UserMenu />
      </UserProvider>
    );

    expect(screen.getByText('Login')).toBeInTheDocument();
  });
});
```

#### Testing Async Components (Server Components)

```typescript
// UserProfile.test.tsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { UserProfile } from './UserProfile';

// Mock fetch
global.fetch = vi.fn();

describe('UserProfile', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders user data', async () => {
    const mockUser = {
      id: '1',
      name: 'Jane Doe',
      email: 'jane@example.com'
    };

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

  it('calls fetch with correct URL', async () => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

    await UserProfile({ userId: '123' });

    expect(global.fetch).toHaveBeenCalledWith(
      'https://api.example.com/users/123',
      expect.any(Object)
    );
  });
});
```

#### Testing Components with User Interactions

```typescript
// SearchInput.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchInput } from './SearchInput';

describe('SearchInput', () => {
  it('calls onSearch after debounce delay', async () => {
    const onSearch = vi.fn();
    const user = userEvent.setup();

    render(<SearchInput onSearch={onSearch} debounceMs={300} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'test query');

    // Should not call immediately
    expect(onSearch).not.toHaveBeenCalled();

    // Wait for debounce
    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test query');
    }, { timeout: 500 });
  });

  it('shows clear button when input has value', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={vi.fn()} />);

    const input = screen.getByRole('textbox');
    await user.type(input, 'search term');

    expect(screen.getByRole('button', { name: /clear/i })).toBeInTheDocument();
  });

  it('clears input when clear button clicked', async () => {
    const user = userEvent.setup();
    render(<SearchInput onSearch={vi.fn()} />);

    const input = screen.getByRole('textbox') as HTMLInputElement;
    await user.type(input, 'search term');

    const clearButton = screen.getByRole('button', { name: /clear/i });
    await user.click(clearButton);

    expect(input.value).toBe('');
  });
});
```

### Testing Best Practices

1. **Test user behavior, not implementation**
2. **Use semantic queries** (getByRole, getByLabelText)
3. **Wait for async operations** with waitFor
4. **Mock external dependencies** (fetch, timers)
5. **Test accessibility** (roles, labels, keyboard navigation)
6. **Keep tests isolated** (clean up between tests)

```typescript
// Good practices example
describe('LoginForm', () => {
  it('shows validation error for invalid email', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={vi.fn()} />);

    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /login/i });

    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);

    expect(await screen.findByText(/invalid email/i)).toBeInTheDocument();
  });
});
```
