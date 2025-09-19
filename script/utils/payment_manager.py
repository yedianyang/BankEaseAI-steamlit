# script/utils/payment_manager.py
import streamlit as st
import stripe
from datetime import datetime, timedelta
import json

class PaymentManager:
    """支付管理器 - 集成Stripe"""
    
    def __init__(self):
        # 从Streamlit secrets获取Stripe密钥
        self.stripe_public_key = st.secrets.get("stripe_public_key", "")
        self.stripe_secret_key = st.secrets.get("stripe_secret_key", "")
        
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
        
        self.plans = {
            'free': {'price': 0, 'files': 5, 'name': '免费版'},
            'pro': {'price': 9.99, 'files': 50, 'name': '专业版'},
            'enterprise': {'price': 29.99, 'files': -1, 'name': '企业版'}
        }
    
    def create_checkout_session(self, user_email, plan_name, success_url, cancel_url):
        """创建Stripe结账会话"""
        if not self.stripe_secret_key:
            st.error("Stripe配置未完成，请联系管理员")
            return None
        
        try:
            # 获取计划信息
            plan_info = self.plans.get(plan_name)
            if not plan_info:
                st.error("无效的订阅计划")
                return None
            
            # 创建价格ID（需要在Stripe Dashboard中创建）
            price_id = self._get_price_id(plan_name)
            if not price_id:
                st.error(f"未找到{plan_name}计划的价格ID")
                return None
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                customer_email=user_email,
                metadata={
                    'plan_name': plan_name,
                    'user_email': user_email
                }
            )
            
            return session.url
            
        except stripe.error.StripeError as e:
            st.error(f"支付处理错误: {str(e)}")
            return None
    
    def _get_price_id(self, plan_name):
        """获取Stripe价格ID"""
        # 这些价格ID需要在Stripe Dashboard中创建
        price_ids = {
            'pro': st.secrets.get("stripe_pro_price_id", ""),
            'enterprise': st.secrets.get("stripe_enterprise_price_id", "")
        }
        return price_ids.get(plan_name)
    
    def handle_webhook(self, payload, sig_header):
        """处理Stripe webhook"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, st.secrets.get("stripe_webhook_secret", "")
            )
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                self._process_successful_payment(session)
            
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                self._process_subscription_cancellation(subscription)
            
            return True
            
        except stripe.error.SignatureVerificationError:
            st.error("Webhook签名验证失败")
            return False
        except Exception as e:
            st.error(f"Webhook处理错误: {str(e)}")
            return False
    
    def _process_successful_payment(self, session):
        """处理成功支付"""
        # 这里需要更新用户订阅状态
        # 实际实现需要根据session中的metadata更新数据库
        pass
    
    def _process_subscription_cancellation(self, subscription):
        """处理订阅取消"""
        # 这里需要更新用户订阅状态
        pass
    
    def get_subscription_info(self, customer_id):
        """获取订阅信息"""
        try:
            subscriptions = stripe.Subscription.list(customer=customer_id)
            if subscriptions.data:
                subscription = subscriptions.data[0]
                return {
                    'status': subscription.status,
                    'current_period_end': subscription.current_period_end,
                    'plan_name': subscription.items.data[0].price.nickname
                }
        except stripe.error.StripeError:
            pass
        return None
    
    def cancel_subscription(self, subscription_id):
        """取消订阅"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError as e:
            st.error(f"取消订阅失败: {str(e)}")
            return False
