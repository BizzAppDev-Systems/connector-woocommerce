from collections import Counter


def get_queue_job_description(model_name, batch=False, job_type=""):
    """Customize queue job description"""
    if batch:
        message = "Prepare Batch {} of ".format(job_type)
    else:
        message = "Record {} of ".format(job_type)
    model_name = model_name.replace("woo", "WooCommerce")
    return "{} {}".format(
        message,
        " ".join(list(Counter(model_name.replace(".", " ").title().split()).keys())),
    )
