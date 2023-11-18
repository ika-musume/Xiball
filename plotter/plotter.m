csv_data = csvread("LOG0_star.csv");
refX = csv_data(:, 1);
refY = csv_data(:, 2);
ballX = csv_data(:, 3);
ballY = csv_data(:, 4);

plot(refX, refY, 'LineWidth', 2); hold;
plot(ballX, ballY, 'LineWidth', 1);