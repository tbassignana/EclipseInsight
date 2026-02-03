import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// Mock framer-motion to avoid animation issues in tests
jest.mock("framer-motion", () => ({
  motion: {
    div: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <div {...props}>{children}</div>
    ),
    p: ({ children, ...props }: React.PropsWithChildren<Record<string, unknown>>) => (
      <p {...props}>{children}</p>
    ),
  },
  AnimatePresence: ({ children }: React.PropsWithChildren) => <>{children}</>,
}));

// Mock AuthContext
const mockLogin = jest.fn();
const mockRegister = jest.fn();
jest.mock("@/context/AuthContext", () => ({
  useAuthContext: () => ({
    user: null,
    token: null,
    isLoading: false,
    isAuthenticated: false,
    login: mockLogin,
    register: mockRegister,
    logout: jest.fn(),
  }),
}));

// Must import AFTER mocks are set up
import LoginPage from "@/app/login/page";
import ForgotPasswordPage from "@/app/forgot-password/page";

describe("LoginPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders login form with email and password fields", () => {
    render(<LoginPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /sign in/i })).toBeInTheDocument();
  });

  it("has a link to forgot password page", () => {
    render(<LoginPage />);
    expect(screen.getByText(/forgot password/i)).toBeInTheDocument();
  });

  it("has a link to registration page", () => {
    render(<LoginPage />);
    expect(screen.getByText(/create an account/i)).toBeInTheDocument();
  });

  it("calls login on form submission", async () => {
    mockLogin.mockResolvedValueOnce(undefined);
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "test@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "password123" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("test@example.com", "password123");
    });
  });

  it("displays error message on login failure", async () => {
    mockLogin.mockRejectedValueOnce(new Error("Invalid credentials"));
    render(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: "bad@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: "wrongpass" },
    });
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
    });
  });
});

describe("ForgotPasswordPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the forgot password form", () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /send reset token/i })).toBeInTheDocument();
  });

  it("has a link back to sign in", () => {
    render(<ForgotPasswordPage />);
    expect(screen.getByText(/back to sign in/i)).toBeInTheDocument();
  });
});
