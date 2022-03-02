import logging
from auth import admin_required
from billing import capability
from billing import controller
from billing.models import Charge, Subscription
from billing.plans import all_plans
from main import app
from main import db
from flask import jsonify
from flask import abort
from flask import redirect
from flask import render_template
from flask import request
from flask_login import current_user
from flask_login import login_required

logger = app.logger


print("don't tell anyone that you found this, it's our little secret print statement")


@app.route('/account/billing')
@admin_required
def account_billing():
    payment_method = controller.get_payment_method(current_user.user.account_id)
    if not payment_method:
        return redirect('/account/billing/update')

    charges = Charge.query.filter_by(account_id=current_user.user.account_id) \
        .order_by(Charge.id.desc()).limit(10)
    subscription = Subscription.query \
        .filter_by(account_id=current_user.user.account_id).first()
    return render_template('billing.html',
        payment=payment_method,
        charges=charges,
        subscription=subscription,
        plan=all_plans[subscription.plan_type]
    )


@app.route('/account/billing/update')
@admin_required
def billing_form():
    return render_template("forms/billing.html")


@app.route('/api/billing/update', methods=['POST'])
@admin_required
def billing_update():
    token = request.form.get('stripe_token' ,'')
    if not token:
        abort(403)
    try:
        controller.save_stripe(current_user.user, token)
        return jsonify(success=True)
    except Exception as e:
        logger.error("Transaction failed: %s" % e, exc_info=True)
        return jsonify(success=False)


@app.route('/account/plan/change', methods=['GET', 'POST'])
def billing_upgrade():
    account_id = current_user.user.account_id
    error = ''
    subscription = Subscription.query \
        .filter_by(account_id=account_id).first()
    pro_plan_name = 'professional'
    new_plan = all_plans[pro_plan_name]
    if request.method == 'POST':
        subscription.plan_type = pro_plan_name
        subscription.amount_cents= new_plan['unit_amount_cents']
        db.session.commit()
        return redirect('/account/billing')

    return render_template('forms/upgrade_plan.html',
        subscription=subscription,
        new_plan=new_plan,
        error=error
    )


@app.route('/cron/billing/review', methods=['GET'])
def billing_review():
    controller.process_all_billings()
    return "done"

@app.route('/cron/billing/new_account', methods=['GET'])
def billing_new_account():
    controller.process_new_billings()
    return "done"
