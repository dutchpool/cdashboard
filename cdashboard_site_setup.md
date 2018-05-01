Setting Up Your Site

You can use a domain name of just use your ip address from your VPS.
First of all, make sure to log back in with your non-root username if you logged out already.

We need to install nginx:

sudo apt-get update

sudo apt-get install nginx

sudo ufw app list

sudo ufw allow 'Nginx HTTP'

sudo systemctl status nginx

You should see that nginx is active and running. Now we need to setup the site.
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/YOURDOMAIN.COM

sudo nano /etc/nginx/sites-available/YOURDOMAIN.com

Change root /var/www/html; to root /home/USERNAME/cdashboard; Add your domain to the line server_name as follows server_name YOURDOMAIN.COM;

Ctrl + x, Y + enter.

Create a symbolic link of your YOURDOMAIN.com to the sites-enabled dir.
sudo ln -s /etc/nginx/sites-available/YOURDOMAIN.COM /etc/nginx/sites-enabled/YOURDOMAIN.COM

Reload nginx to make sure all changes are reloaded
sudo systemctl reload nginx

You can logout if you want.

Reminder for Microsoft Azure users: don't forget to open port 80, if not already done.

Now for the last step, you need to go to your domain providers control panel to edit your DNS records. 
Simply create a new A record which points to your VPS’ IP Address. Then, you’re done! 
Wait for your DNS records to update and you should be able to see your Dashboard site by typing in your domain name.

Congratulations on setting up your Crypto Dashboard.