import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Card, CardContent } from "@/components/ui/card";
import { Shield, UserPlus, LogIn } from "lucide-react";

const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(6, "Password must be at least 6 characters"),
});

const signupSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  email: z.string().email("Please enter a valid email address"),
  organization: z.string().optional(),
  password: z.string().min(6, "Password must be at least 6 characters"),
  acceptTerms: z.boolean().refine(val => val === true, "You must accept the terms"),
});

interface AuthModalProps {
  onLogin: (email: string, password: string) => Promise<any>;
  onSignup: (data: any) => Promise<any>;
  isLoading: boolean;
}

export function AuthModal({ onLogin, onSignup, isLoading }: AuthModalProps) {
  const [isSignup, setIsSignup] = useState(false);

  const loginForm = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const signupForm = useForm({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      firstName: "",
      lastName: "",
      email: "",
      organization: "",
      password: "",
      acceptTerms: false,
    },
  });

  const handleLogin = async (data: z.infer<typeof loginSchema>) => {
    await onLogin(data.email, data.password);
  };

  const handleSignup = async (data: z.infer<typeof signupSchema>) => {
    await onSignup(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" data-testid="auth-modal">
      <Card className="w-full max-w-md">
        <CardContent className="p-8">
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-blue-700 rounded-full flex items-center justify-center mb-4">
              <Shield className="text-white text-2xl" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">LegalTech Pro</h1>
            <p className="text-gray-600">Secure Legal Document Management</p>
          </div>

          {!isSignup ? (
            <div data-testid="login-form">
              <form onSubmit={loginForm.handleSubmit(handleLogin)} className="space-y-6">
                <div>
                  <Label htmlFor="login-email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </Label>
                  <Input
                    id="login-email"
                    type="email"
                    {...loginForm.register("email")}
                    placeholder="Enter your email"
                    className="w-full"
                    data-testid="input-login-email"
                  />
                  {loginForm.formState.errors.email && (
                    <p className="text-red-500 text-sm mt-1">{loginForm.formState.errors.email.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="login-password" className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </Label>
                  <Input
                    id="login-password"
                    type="password"
                    {...loginForm.register("password")}
                    placeholder="Enter your password"
                    className="w-full"
                    data-testid="input-login-password"
                  />
                  {loginForm.formState.errors.password && (
                    <p className="text-red-500 text-sm mt-1">{loginForm.formState.errors.password.message}</p>
                  )}
                </div>
                <Button
                  type="submit"
                  className="w-full bg-blue-700 text-white py-3 rounded-lg font-medium hover:bg-blue-800"
                  disabled={isLoading}
                  data-testid="button-login"
                >
                  <LogIn className="mr-2 h-4 w-4" />
                  {isLoading ? "Signing In..." : "Sign In"}
                </Button>
              </form>
              <div className="text-center mt-6">
                <button
                  className="text-blue-700 hover:underline"
                  onClick={() => setIsSignup(true)}
                  data-testid="link-signup"
                >
                  Don't have an account? Sign up
                </button>
              </div>
            </div>
          ) : (
            <div data-testid="signup-form">
              <form onSubmit={signupForm.handleSubmit(handleSignup)} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                      First Name
                    </Label>
                    <Input
                      id="firstName"
                      {...signupForm.register("firstName")}
                      placeholder="John"
                      data-testid="input-first-name"
                    />
                    {signupForm.formState.errors.firstName && (
                      <p className="text-red-500 text-sm mt-1">{signupForm.formState.errors.firstName.message}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                      Last Name
                    </Label>
                    <Input
                      id="lastName"
                      {...signupForm.register("lastName")}
                      placeholder="Doe"
                      data-testid="input-last-name"
                    />
                    {signupForm.formState.errors.lastName && (
                      <p className="text-red-500 text-sm mt-1">{signupForm.formState.errors.lastName.message}</p>
                    )}
                  </div>
                </div>
                <div>
                  <Label htmlFor="signup-email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </Label>
                  <Input
                    id="signup-email"
                    type="email"
                    {...signupForm.register("email")}
                    placeholder="john.doe@lawfirm.com"
                    data-testid="input-signup-email"
                  />
                  {signupForm.formState.errors.email && (
                    <p className="text-red-500 text-sm mt-1">{signupForm.formState.errors.email.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="organization" className="block text-sm font-medium text-gray-700 mb-2">
                    Organization
                  </Label>
                  <Input
                    id="organization"
                    {...signupForm.register("organization")}
                    placeholder="Law Firm Name"
                    data-testid="input-organization"
                  />
                </div>
                <div>
                  <Label htmlFor="signup-password" className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </Label>
                  <Input
                    id="signup-password"
                    type="password"
                    {...signupForm.register("password")}
                    placeholder="Create a strong password"
                    data-testid="input-signup-password"
                  />
                  {signupForm.formState.errors.password && (
                    <p className="text-red-500 text-sm mt-1">{signupForm.formState.errors.password.message}</p>
                  )}
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="acceptTerms"
                    checked={signupForm.watch("acceptTerms")}
                    onCheckedChange={(checked) => signupForm.setValue("acceptTerms", checked === true)}
                    data-testid="checkbox-terms"
                  />
                  <Label htmlFor="acceptTerms" className="text-sm text-gray-700">
                    I agree to the Terms of Service and Privacy Policy
                  </Label>
                </div>
                {signupForm.formState.errors.acceptTerms && (
                  <p className="text-red-500 text-sm">{signupForm.formState.errors.acceptTerms.message}</p>
                )}
                <Button
                  type="submit"
                  className="w-full bg-blue-700 text-white py-3 rounded-lg font-medium hover:bg-blue-800"
                  disabled={isLoading}
                  data-testid="button-signup"
                >
                  <UserPlus className="mr-2 h-4 w-4" />
                  {isLoading ? "Creating Account..." : "Create Account"}
                </Button>
              </form>
              <div className="text-center mt-6">
                <button
                  className="text-blue-700 hover:underline"
                  onClick={() => setIsSignup(false)}
                  data-testid="link-login"
                >
                  Already have an account? Sign in
                </button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
