"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, CheckCircle2, ArrowLeft } from "lucide-react";
import { useState } from "react";
import api from "@/lib/api";

const forgotPasswordSchema = z.object({
  email: z.string().email({ message: "Please enter a valid email address" }),
});

type ForgotPasswordFormValues = z.infer<typeof forgotPasswordSchema>;

export default function ForgotPasswordPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const form = useForm<ForgotPasswordFormValues>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: {
      email: "",
    },
  });

  const onSubmit = async (data: ForgotPasswordFormValues) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await api.post("/auth/forgot-password", { email: data.email });
      setSuccess(true);
    } catch (err: any) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to send reset email"
      );
    } finally {
      setIsLoading(false);
    }
  };

  if (success) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Check Your Email</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="success">
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              If an account exists with the email you provided, you will receive
              a password reset link shortly.
            </AlertDescription>
          </Alert>
        </CardContent>
        <CardFooter>
          <Button asChild className="w-full">
            <Link href="/login">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Sign In
            </Link>
          </Button>
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Forgot Password</CardTitle>
        <CardDescription>
          Enter your email address and we&apos;ll send you a link to reset your
          password
        </CardDescription>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input
                      type="email"
                      placeholder="name@example.com"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Sending..." : "Send Reset Link"}
            </Button>
          </form>
        </Form>
      </CardContent>
      <CardFooter className="flex justify-center">
        <Link
          href="/login"
          className="text-sm text-primary hover:underline flex items-center"
        >
          <ArrowLeft className="mr-1 h-3 w-3" />
          Back to Sign In
        </Link>
      </CardFooter>
    </Card>
  );
}
