export interface User {
  id: number;
  name: string;
  email: string;
  created_at: string;
}

export interface Expense {
  id: number;
  user_id: number;
  crop_type: string;
  seed_cost: number;
  fertilizer_cost: number;
  labor_cost: number;
  irrigation_cost: number;
  transport_cost: number;
  other_cost: number;
  farm_size: number;
  date: string;
  created_at: string;
  total: number;
}

export interface ExpenseCreate {
  crop_type: string;
  seed_cost: number;
  fertilizer_cost: number;
  labor_cost: number;
  irrigation_cost: number;
  transport_cost: number;
  other_cost: number;
  farm_size: number;
  date: string;
}

export interface Income {
  id: number;
  user_id: number;
  crop_type: string;
  amount: number;
  quantity: number;
  date: string;
  expense_id: number | null;
  created_at: string;
  is_paired: boolean;
}

export interface IncomeCreate {
  crop_type: string;
  amount: number;
  quantity: number;
  date: string;
  expense_id?: number | null;
}

export interface Prediction {
  id: number;
  user_id: number;
  crop_type: string;
  seed_cost: number;
  fertilizer_cost: number;
  labor_cost: number;
  irrigation_cost: number;
  transport_cost: number;
  farm_size: number;
  predicted_revenue: number;
  predicted_profit: number;
  model_used: string;
  created_at: string;
}

export interface PredictionRequest {
  crop_type: string;
  seed_cost: number;
  fertilizer_cost: number;
  labor_cost: number;
  irrigation_cost: number;
  transport_cost: number;
  farm_size: number;
}

export interface Report {
  total_expense: number;
  total_income: number;
  net_profit: number;
  expense_by_crop: Record<string, number>;
  income_by_crop: Record<string, number>;
}

export interface Token {
  access_token: string;
  token_type: string;
}
